import os
from django_serialization_benchmarks.data_generation import generate_benchmark_json


def main():
    # Resolve project root relative to this script
    DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.dirname(DIR)
    SAMPLE_DATA_DIR = os.path.join(ROOT, "sample_data")

    # Ensure sample_data directory exists
    os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)

    CONFIGS = [
        "10 0 0",
        "10 5 5",
        "10 10 5",
        "100 0 0",
        "100 5 5",
        "100 10 5",
        "1000 0 0",
        "1000 5 5",
        "1000 10 5",
        "1000 10 10",
        "10000 0 0",
        "10000 5 5",
    ]

    for config in CONFIGS:
        x, y, z = map(int, config.split())
        filename = f"benchmark_data_{x}_{y}_{z}.json"
        filepath = os.path.join(SAMPLE_DATA_DIR, filename)
        print(f"Generating {filepath}...")
        generate_benchmark_json(x, y, z, filepath)
    print("Done!")


if __name__ == "__main__":
    main()
