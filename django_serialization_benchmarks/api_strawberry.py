import json
import os
from pathlib import Path
from typing import List, Dict

import strawberry

from .types_strawberry import BenchmarkRootStrawberry, _to_root_obj
from .types_pydantic import load_pydantic_data, get_json_path, BenchmarkRootPydanticType

# ---- Cache for memoization ----

_vanilla_cache: Dict[str, List[BenchmarkRootStrawberry]] = {}


# ---- Query definition ----


@strawberry.type
class BenchmarkDataQuery:
    @strawberry.field()
    def benchmark_vanilla_types(
        self, filename: str = "benchmark_data_100_5_5.json"
    ) -> List[BenchmarkRootStrawberry]:
        """Load data from the generated JSON file and return it as-is using Strawberry types."""
        if filename in _vanilla_cache:
            return _vanilla_cache[filename]

        json_path = get_json_path(filename)
        if not json_path.exists():
            return []

        raw = json.loads(json_path.read_text(encoding="utf-8"))
        data = [_to_root_obj(item) for item in raw]
        _vanilla_cache[filename] = data
        return data

    @strawberry.field()
    def benchmark_pydantic_types(
        self, filename: str = "benchmark_data_100_5_5.json"
    ) -> List[BenchmarkRootPydanticType]:
        """Load data from the generated JSON file and return it as-is using Pydantic models."""
        return load_pydantic_data(filename)


schema = strawberry.Schema(query=BenchmarkDataQuery)
