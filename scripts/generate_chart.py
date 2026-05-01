import os
import yaml
import matplotlib.pyplot as plt

import sys

import argparse


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
    all_sizes = set()
    num_measured = None

    for filename in files:
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r") as f:
            content = yaml.safe_load(f)
            average = content.get("average", 0)
            endpoint = content.get("endpoint", "")

            d_size = content.get("dataset_size")
            dn_size = content.get("dataset_nested_size")
            dn2_size = content.get("dataset_nested2_size")
            size_triplet = (d_size, dn_size, dn2_size)
            all_sizes.add(size_triplet)

            if num_measured is None:
                num_measured = content.get("num_measured")

            data.append(
                {
                    "average": average,
                    "endpoint": endpoint,
                    "size_triplet": size_triplet,
                }
            )

    # Sort: alphabetical order by endpoint name, then by size
    data.sort(key=lambda x: (x["endpoint"], x["size_triplet"]))

    unique_sizes = sorted(list(all_sizes))
    all_same_size = len(unique_sizes) == 1

    labels = []
    for d in data:
        if all_same_size:
            labels.append(d["endpoint"])
        else:
            s = d["size_triplet"]
            labels.append(f"{d['endpoint']} ({s[0]}_{s[1]}_{s[2]})")

    averages = [d["average"] for d in data]

    plt.figure(figsize=(12, 8))
    bars = plt.bar(labels, averages, color="skyblue")

    plt.xlabel("Endpoint")
    plt.ylabel("Average Time (s)")

    if all_same_size:
        dataset_size, dataset_nested_size, dataset_nested2_size = unique_sizes[0]
        title_parts = []
        title_parts.append(f"Objs={dataset_size}")
        title_parts.append(f"Nested Objs={dataset_nested_size}")
        title_parts.append(f"Subnested Objs={dataset_nested2_size}")
        total = (
            dataset_size
            + (dataset_size * dataset_nested_size)
            + (dataset_size * dataset_nested_size * dataset_nested2_size)
        )
        title_parts.append(f"Total objs={total}")
        title = "Benchmark Results: " + ", ".join(title_parts)
    else:
        size_strs = [f"({s[0]},{s[1]},{s[2]})" for s in unique_sizes]
        title = "Benchmark Results: Sizes=" + ", ".join(size_strs)

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
