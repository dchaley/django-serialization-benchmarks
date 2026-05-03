import argparse
import os
import sys

# Ensure the scripts directory is in the path so we can import other scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_benchmark import run_benchmark
from generate_chart import generate_chart, load_series_data

def main():
    parser = argparse.ArgumentParser(description="Run benchmarks for a specific scenario.")
    parser.add_argument(
        "--scenario-name",
        type=str,
        required=True,
        help="Name of the benchmark scenario (e.g., 1000_5_5)",
    )
    parser.add_argument(
        "--data-file",
        type=str,
        required=True,
        help="The sample data JSON file to use",
    )
    parser.add_argument(
        "--num-measured",
        type=int,
        default=20,
        help="Number of benchmark measurements to take (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Base directory for results (default: results)",
    )

    args = parser.parse_args()

    # Resolve project root
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timing_dir = os.path.join(ROOT, args.output_dir, "timing")
    charts_dir = os.path.join(ROOT, args.output_dir, "charts")

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

    print(f"Starting benchmark scenario: {args.scenario_name}")
    print(f"Data file: {args.data_file}")
    print(f"Measurements: {args.num_measured}")
    sys.stdout.flush()

    output_files = []
    for endpoint in endpoints:
        output_file = os.path.join(timing_dir, f"{endpoint}_{args.scenario_name}.yaml")
        run_benchmark(
            benchmarks=args.num_measured,
            endpoint=endpoint,
            output_file=output_file,
            filename=args.data_file,
            scenario_name=args.scenario_name,
        )
        output_files.append(output_file)

    print("\nGenerating chart...")
    chart_output = os.path.join(charts_dir, f"endpoints_{args.scenario_name}.png")

    # Use the generate_chart signature from origin/main
    all_series_data = [load_series_data(output_files)]
    series_labels = [args.scenario_name]

    generate_chart(
        all_series=all_series_data,
        series_labels=series_labels,
        output_filename=chart_output
    )
    print(f"Benchmark scenario '{args.scenario_name}' complete.")

if __name__ == "__main__":
    main()
