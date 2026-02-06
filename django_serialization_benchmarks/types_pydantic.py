import datetime
import json
import uuid
from pathlib import Path
from typing import List, Dict
import strawberry
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

# Cache for memoization
_pydantic_cache: Dict[str, List["BenchmarkRootPydantic"]] = {}


def get_json_path(filename: str) -> Path:
    """Resolve path: construct filename based on parameters and look in sample_data/"""
    project_root = Path(__file__).resolve().parent.parent
    sample_data_dir = project_root / "sample_data"
    return sample_data_dir / filename


def load_pydantic_data(filename: str) -> List["BenchmarkRootPydantic"]:
    """Load data from the generated JSON file and return it as-is using Pydantic models with memoization."""
    if filename in _pydantic_cache:
        return _pydantic_cache[filename]

    json_path = get_json_path(filename)
    if not json_path.exists():
        return []

    raw = json.loads(json_path.read_text(encoding="utf-8"))
    data = [BenchmarkRootPydantic(**item) for item in raw]
    _pydantic_cache[filename] = data
    return data


class BenchmarkNested2Pydantic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: uuid.UUID
    metric_name: str
    metric_value: int
    is_active: bool
    created_at: datetime.datetime


class BenchmarkNestedPydantic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: uuid.UUID
    label: str
    value: int
    is_internal: bool
    score: float
    notes: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    priority: int
    category_code: str
    nested2_objects: List[BenchmarkNested2Pydantic]


class BenchmarkRootPydantic(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: uuid.UUID
    index: int
    name: str
    description: str
    category: str
    owner: str
    created_at_epoch: int
    updated_at_epoch: int
    version: int
    status: str
    nested_objects: List[BenchmarkNestedPydantic]


@strawberry.experimental.pydantic.type(model=BenchmarkNested2Pydantic, all_fields=True)
class BenchmarkNested2PydanticType:
    pass


@strawberry.experimental.pydantic.type(model=BenchmarkNestedPydantic, all_fields=True)
class BenchmarkNestedPydanticType:
    pass


@strawberry.experimental.pydantic.type(model=BenchmarkRootPydantic, all_fields=True)
class BenchmarkRootPydanticType:
    pass
