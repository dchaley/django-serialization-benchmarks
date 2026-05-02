import subprocess
import time
import requests
import statistics
import yaml
import sys
import argparse
import os

import re


def run_benchmark(
    warmups=3,
    benchmarks=20,
    endpoint="strawberry_vanilla",
    output_file=None,
    filename="benchmark_data_100_5_5.json",
    scenario_name=None,
):
    print("–––––––––––––––––––––––")
    print(f"Benchmarking {endpoint} with data file {filename}...")
    # 1. Start the Django API
    print("Startup")
    print(f"  Killing any existing process on port 8001...")
    subprocess.run(
        "lsof -t -i :8001 | xargs kill -9 2>/dev/null || true", shell=True, check=False
    )
    print(f"  Starting Django server...")
    manage_py = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "manage.py")
    )
    server_process = subprocess.Popen(
        [sys.executable, manage_py, "runserver", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    graphql_query = None
    if endpoint == "strawberry_vanilla" or endpoint == "strawberry_pydantic":
        url = "http://127.0.0.1:8001/graphql/"
        field_name = (
            "benchmarkVanillaTypes"
            if endpoint == "strawberry_vanilla"
            else "benchmarkPydanticTypes"
        )
        graphql_query = f"""
        query BenchmarkDataQuery {{
          {field_name}(filename: "{filename}") {{
            id
            index
            name
            description
            category
            owner
            createdAtEpoch
            updatedAtEpoch
            version
            status
            nestedObjects {{
              id
              label
              value
              isInternal
              score
              notes
              createdAt
              updatedAt
              priority
              categoryCode
              nested2Objects {{
                id
                metricName
                metricValue
                isActive
                createdAt
              }}
            }}
          }}
        }}
        """
    elif endpoint == "ninja_pydantic":
        url = f"http://127.0.0.1:8001/api/ninja-benchmark/{filename}"
    elif endpoint == "drf_pydantic_serializer":
        url = f"http://127.0.0.1:8001/api/drf-pydantic-benchmark/{filename}"
    elif endpoint == "drf_model_dump":
        url = f"http://127.0.0.1:8001/api/drf-json-benchmark/{filename}"
    elif endpoint == "drf_renderer_pydantic_model_dump":
        url = f"http://127.0.0.1:8001/api/drf-pydantic-model-dump-renderer-benchmark/{filename}"
    elif endpoint == "drf_renderer_pydantic_model_dump_json":
        url = f"http://127.0.0.1:8001/api/drf-pydantic-json-renderer-benchmark/{filename}"
    elif endpoint == "pydantic_http_response":
        url = f"http://127.0.0.1:8001/api/pydantic-http-response-benchmark/{filename}"
    else:
        raise ValueError(f"Unknown endpoint: {endpoint}")

    def make_request(request_url, query=None):
        if query:
            return requests.post(request_url, json={"query": query})
        return requests.get(request_url)

    # Wait for server to be ready
    max_retries = 10
    ready = False
    for i in range(max_retries):
        try:
            # Simple heartbeat check
            if graphql_query:
                response = requests.post(
                    url, json={"query": "{ __schema { queryType { name } } }"}
                )
            elif endpoint == "ninja_pydantic":
                response = requests.get(f"http://127.0.0.1:8001/api/docs")
            else:
                response = requests.get(url)

            if response.status_code == 200:
                ready = True
                print("  Server is ready.")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    if not ready:
        print("  Server failed to start.")
        server_process.terminate()
        return

    # 2. Warm-up calls
    print("Benchmarking")
    print(f"  Running {warmups} warm-up calls...")
    for _ in range(warmups):
        make_request(url, graphql_query)

    # 3. Benchmark calls
    print(f"  Running {benchmarks} benchmark calls...")
    latencies = []
    for i in range(benchmarks):
        start_time = time.perf_counter()
        response = make_request(url, graphql_query)
        end_time = time.perf_counter()

        if response.status_code == 200:
            latencies.append(end_time - start_time)
        else:
            print(
                f"Error in benchmark call {i}: {response.status_code} {response.text}"
            )

    # Shutdown server
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()

    if not latencies:
        print("No successful benchmark calls.")
        return

    # 4. Output yaml report
    dataset_size = None
    dataset_nested_size = None
    dataset_nested2_size = None

    # Parse filename for sizes: benchmark_data_<num_rows>_<num_nested>_<num_subnested>.json
    match = re.search(r"benchmark_data_(\d+)_(\d+)_(\d+)\.json", filename)
    if match:
        dataset_size = int(match.group(1))
        dataset_nested_size = int(match.group(2))
        dataset_nested2_size = int(match.group(3))

    stats = {
        "endpoint": endpoint,
        "scenario_name": scenario_name,
        "num_measured": benchmarks,
        "dataset_size": dataset_size,
        "dataset_nested_size": dataset_nested_size,
        "dataset_nested2_size": dataset_nested2_size,
        "filename": filename,
        "average": float(statistics.mean(latencies)),
        "min": float(min(latencies)),
        "p25": (
            float(statistics.quantiles(latencies, n=4)[0])
            if len(latencies) >= 2
            else float(statistics.median(latencies))
        ),
        "p50": float(statistics.median(latencies)),
        "p75": (
            float(statistics.quantiles(latencies, n=4)[2])
            if len(latencies) >= 2
            else float(statistics.median(latencies))
        ),
        "max": float(max(latencies)),
        "std_dev": float(statistics.stdev(latencies)) if len(latencies) > 1 else 0.0,
        # 'benchmark_values': [float(v) for v in latencies],
    }

    yaml_output = yaml.dump(stats, sort_keys=False)

    if output_file:
        with open(output_file, "w") as f:
            f.write(yaml_output)
        print("Results")
        print(f"  Avg: {stats['average']:.4f}s")
        print(f"  --> {output_file}")
    else:
        print(yaml_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GraphQL benchmarks.")
    parser.add_argument(
        "--num-warmup", type=int, default=3, help="Number of warm-up calls"
    )
    parser.add_argument(
        "--num-measured", type=int, default=20, help="Number of benchmark calls"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        choices=[
            "strawberry_vanilla",
            "strawberry_pydantic",
            "ninja_pydantic",
            "drf_pydantic_serializer",
            "drf_model_dump",
            "drf_renderer_pydantic_model_dump",
            "drf_renderer_pydantic_model_dump_json",
            "pydantic_http_response",
        ],
        default="strawberry_vanilla",
        help="Endpoint to benchmark",
    )
    parser.add_argument(
        "--output-file", type=str, help="Optional file to save the YAML report"
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="benchmark_data_100_5_5.json",
        help="Specific filename to load from sample_data/",
    )
    parser.add_argument(
        "--scenario-name",
        type=str,
        help="The name of the benchmark scenario",
    )
    args = parser.parse_args()

    run_benchmark(
        warmups=args.num_warmup,
        benchmarks=args.num_measured,
        endpoint=args.endpoint,
        output_file=args.output_file,
        filename=args.filename,
        scenario_name=args.scenario_name,
    )
