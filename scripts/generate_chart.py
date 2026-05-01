import os
import yaml
import re
import matplotlib.pyplot as plt

import sys

import argparse


def get_dataset_size(filename):
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


def generate_chart(suffix=None, output_filename=None, input_dir="results"):
    if suffix:
        pattern = f"_{suffix}.yaml"
        files = [f for f in os.listdir(input_dir) if f.endswith(pattern)]
        if not output_filename:
            output_filename = f"benchmark_chart_{suffix}.png"
    else:
        files = [f for f in os.listdir(input_dir) if f.endswith(".yaml")]
        if not output_filename:
            output_filename = "benchmark_chart.png"

    if not files:
        print(
            f"No files found for suffix: {suffix}"
            if suffix
            else f"No yaml files found in {input_dir}/"
        )
        return

    data = []
    num_measured = None
    dataset_size = None
    dataset_nested_size = None
    dataset_nested2_size = None

    for filename in files:
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r") as f:
            content = yaml.safe_load(f)
            # Remove .yaml extension for the label
            label = filename.replace(".yaml", "")
            average = content.get("average", 0)
            endpoint = content.get("endpoint", "")
            if num_measured is None:
                num_measured = content.get("num_measured")
            if dataset_size is None:
                dataset_size = content.get("dataset_size")
            if dataset_nested_size is None:
                dataset_nested_size = content.get("dataset_nested_size")
            if dataset_nested2_size is None:
                dataset_nested2_size = content.get("dataset_nested2_size")

            data.append(
                {
                    "label": label,
                    "average": average,
                    "dataset_size": get_dataset_size(filename),
                    "endpoint": endpoint,
                }
            )

    # Sort: alphabetical order by endpoint name
    data.sort(key=lambda x: x["endpoint"])

    labels = [d["label"] for d in data]
    averages = [d["average"] for d in data]

    plt.figure(figsize=(12, 8))
    bars = plt.bar(labels, averages, color="skyblue")

    plt.xlabel("Benchmark Configuration")
    plt.ylabel("Average Time (s)")

    title_parts = []
    title_parts.append(f"Objs={dataset_size}")
    title_parts.append(f"Nested Objs={dataset_nested_size}")
    title_parts.append(f"Subnested Objs={dataset_nested2_size}")
    title_parts.append(
        f"Total objs={dataset_size + dataset_size * dataset_nested_size + dataset_size * dataset_nested_size * dataset_nested2_size}"
    )

    title = "Benchmark Results: " + ", ".join(title_parts)
    if num_measured is not None:
        title += f" (Measurements={num_measured})"
    plt.title(title)
    plt.xticks(rotation=45, ha="right")

    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            round(yval, 4),
            va="bottom",
            ha="center",
        )

    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Chart saved to {output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate benchmark charts.")
    parser.add_argument(
        "suffix", nargs="?", default=None, help="Suffix to filter benchmark files"
    )
    parser.add_argument("--output", help="Output filename for the chart")
    parser.add_argument(
        "--input-dir", default="results", help="Directory to look for benchmark files"
    )

    args = parser.parse_args()
    generate_chart(args.suffix, args.output, args.input_dir)
