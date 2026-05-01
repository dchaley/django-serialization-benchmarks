#!/bin/bash

# Resolve script directory and project root
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"

mkdir -p "${ROOT}/results/timing"
mkdir -p "${ROOT}/results/charts"

ENDPOINTS=("strawberry_vanilla" "strawberry_pydantic" "ninja_pydantic" "drf_pydantic" "drf_json" "drf_pydantic_model_dump_renderer" "drf_pydantic_json_renderer" "pydantic_http_response")
CONFIGS=(
    "10 0 0"
    "10 5 5"
    "10 10 5"
    "100 0 0"
    "100 5 5"
    "100 10 5"
    "1000 0 0"
    "1000 5 5"
    "1000 10 5"
    "1000 10 10"
    "10000 5 5"
)
NUM_MEASURED=${1:-50}

for config in "${CONFIGS[@]}"; do
    read -r size l1 l2 <<< "$config"
    suffix="${size}_${l1}_${l2}"
    for endpoint in "${ENDPOINTS[@]}"; do
        "${ROOT}/.venv/bin/python" "${DIR}/run_benchmark.py" --endpoint "$endpoint" --filename "benchmark_data_${suffix}.json" --output-file "${ROOT}/results/timing/${endpoint}_${suffix}.yaml" --num-measured "$NUM_MEASURED"
    done
    "${ROOT}/.venv/bin/python3" "${DIR}/generate_chart.py" "${suffix}" --input-dir "${ROOT}/results/timing" --output "${ROOT}/results/charts/endpoints_${suffix}.png"
done
