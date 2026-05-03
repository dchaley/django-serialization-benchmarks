import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Orchestrate benchmarks for a specific scenario.")
    parser.add_argument(
        "--scenario-name",
        type=str,
        required=True,
        help="Name of the scenario (e.g., 1000_5_5)",
    )
    parser.add_argument(
        "--data-file",
        type=str,
        required=True,
        help="Path to the data file relative to sample_data/ or absolute path",
    )
    parser.add_argument(
        "--num-measured",
        type=int,
        default=20,
        help="Number of benchmark calls (default: 20)",
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)

    timing_dir = os.path.join(root_dir, "results", "timing")
    charts_dir = os.path.join(root_dir, "results", "charts")

    os.makedirs(timing_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)

    endpoints = [
        "strawberry_vanilla",
        "strawberry_pydantic",
        "ninja_pydantic",
        "drf_pydantic_serializer",
        "drf_model_dump",
        "drf_renderer_pydantic_model_dump",
        "drf_renderer_pydantic_model_dump_json",
        "pydantic_http_response",
    ]

    data_file = args.data_file
    # If the data_file is just a name, assume it's in sample_data/
    if not os.path.isabs(data_file) and not data_file.startswith("sample_data/"):
        data_file_path = os.path.join("sample_data", data_file)
    else:
        data_file_path = data_file

    data_file_name = os.path.basename(data_file_path)

    result_files = []
    for endpoint in endpoints:
        output_file = os.path.join(timing_dir, f"{endpoint}_{args.scenario_name}.yaml")
        print(f"Running benchmark for {endpoint}...")

        cmd = [
            sys.executable,
            os.path.join(script_dir, "run_benchmark.py"),
            "--endpoint", endpoint,
            "--filename", data_file_name,
            "--output-file", output_file,
            "--num-measured", str(args.num_measured),
            "--scenario-name", args.scenario_name,
        ]

        subprocess.run(cmd, check=True)
        result_files.append(output_file)

    # Generate chart
    chart_output = os.path.join(charts_dir, f"endpoints_{args.scenario_name}.png")
    print(f"Generating chart: {chart_output}")

    chart_cmd = [
        sys.executable,
        os.path.join(script_dir, "generate_chart.py"),
        "--series"
    ] + result_files + [
        "--output", chart_output
    ]

    subprocess.run(chart_cmd, check=True)
    print("Done!")

if __name__ == "__main__":
    main()
