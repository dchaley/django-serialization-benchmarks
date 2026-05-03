import os
import yaml
import matplotlib.pyplot as plt

import sys

import argparse


import numpy as np


def load_series_data(files):
    data = []
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}")
            continue
        with open(filepath, "r") as f:
            content = yaml.safe_load(f)
            data.append(content)
    return data


def generate_chart(all_series, series_labels, output_filename=None):
    if not all_series:
        print("No data series provided.")
        return

    if not output_filename:
        output_filename = "benchmark_chart.png"

    # Identify all unique endpoints across all series
    endpoints = set()
    for series in all_series:
        for entry in series:
            endpoints.add(entry.get("endpoint", "unknown"))
    endpoints = sorted(list(endpoints))

    # Prepare data for plotting
    num_series = len(all_series)
    num_endpoints = len(endpoints)
    x = np.arange(num_endpoints)
    width = 0.8 / num_series

    fig, ax = plt.subplots(figsize=(12, 8))

    for i, (series, label) in enumerate(zip(all_series, series_labels)):
        mapping = {entry.get("endpoint", "unknown"): entry.get("average", 0) for entry in series}
        averages = [mapping.get(endpoint, 0) for endpoint in endpoints]

        offset = (i - (num_series - 1) / 2) * width
        bars = ax.bar(x + offset, averages, width, label=label)

        # Add values on top of bars
        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    yval,
                    f"{yval:.4f}",
                    va="bottom",
                    ha="center",
                    fontsize=8,
                    rotation=90 if num_series > 2 else 0
                )

    ax.set_xlabel("Endpoint")
    ax.set_ylabel("Average Time (s)")
    ax.set_title("Benchmark Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(endpoints, rotation=45, ha="right")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Chart saved to {output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate benchmark charts.")
    parser.add_argument(
        "--series",
        required=True,
        action="append",
        nargs="+",
        help="One or more files for a data series. Can be specified multiple times."
    )
    parser.add_argument(
        "--series-label",
        action="append",
        help="Label for each series specified with --series."
    )
    parser.add_argument("--output", help="Output filename for the chart")

    args = parser.parse_args()

    all_series_data = []
    series_labels = []

    for i, series_files in enumerate(args.series):
        data = load_series_data(series_files)
        if data:
            all_series_data.append(data)
            if args.series_label and i < len(args.series_label):
                series_labels.append(args.series_label[i])
            else:
                # Default label: use size suffix if all files in series have the same one
                suffixes = set()
                for f in series_files:
                    import re
                    match = re.search(r"_(\d+_\d+_\d+)\.yaml$", f)
                    if match:
                        suffixes.add(match.group(1))

                if len(suffixes) == 1:
                    series_labels.append(list(suffixes)[0])
                else:
                    series_labels.append(f"Series {i + 1}")

    generate_chart(all_series_data, series_labels, args.output)
