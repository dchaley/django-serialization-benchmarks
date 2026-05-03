#!/bin/bash

# Resolve script directory and project root
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"

mkdir -p "${ROOT}/results/timing"
mkdir -p "${ROOT}/results/charts"

ENDPOINTS=("strawberry_vanilla" "strawberry_pydantic" "ninja_pydantic" "drf_pydantic_serializer" "drf_model_dump" "drf_renderer_pydantic_model_dump" "drf_renderer_pydantic_model_dump_json" "pydantic_http_response")
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
    FILES=()
    for endpoint in "${ENDPOINTS[@]}"; do
        OUT_FILE="${ROOT}/results/timing/${endpoint}_${suffix}.yaml"
        python3 "${DIR}/run_benchmark.py" --endpoint "$endpoint" --filename "benchmark_data_${suffix}.json" --output-file "$OUT_FILE" --num-measured "$NUM_MEASURED"
        FILES+=("$OUT_FILE")
    done
    python3 "${DIR}/generate_chart.py" --series "${FILES[@]}" --output "${ROOT}/results/charts/endpoints_${suffix}.png"
done
