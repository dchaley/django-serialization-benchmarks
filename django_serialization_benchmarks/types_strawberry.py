import datetime
import uuid
from typing import List
import strawberry


def _to_nested2_obj(d: dict) -> "BenchmarkNested2Strawberry":
    return BenchmarkNested2Strawberry(
        id=uuid.UUID(d["id"]) if isinstance(d.get("id"), str) else d["id"],
        metric_name=d["metric_name"],
        metric_value=int(d["metric_value"]),
        is_active=bool(d["is_active"]),
        created_at=(
            datetime.datetime.fromisoformat(d["created_at"])
            if isinstance(d["created_at"], str)
            else d["created_at"]
        ),
    )


def _to_nested_obj(d: dict) -> "BenchmarkNestedStrawberry":
    return BenchmarkNestedStrawberry(
        id=uuid.UUID(d["id"]) if isinstance(d.get("id"), str) else d["id"],
        label=d["label"],
        value=int(d["value"]),
        is_internal=bool(d["is_internal"]),
        score=float(d["score"]),
        notes=d["notes"],
        created_at=(
            datetime.datetime.fromisoformat(d["created_at"])
            if isinstance(d["created_at"], str)
            else d["created_at"]
        ),
        updated_at=(
            datetime.datetime.fromisoformat(d["updated_at"])
            if isinstance(d["updated_at"], str)
            else d["updated_at"]
        ),
        priority=int(d["priority"]),
        category_code=d["category_code"],
        nested2_objects=[_to_nested2_obj(x) for x in d.get("nested2_objects", [])],
    )


def _to_root_obj(d: dict) -> "BenchmarkRootStrawberry":
    return BenchmarkRootStrawberry(
        id=uuid.UUID(d["id"]) if isinstance(d.get("id"), str) else d["id"],
        index=int(d["index"]),
        name=d["name"],
        description=d["description"],
        category=d["category"],
        owner=d["owner"],
        created_at_epoch=int(d["created_at_epoch"]),
        updated_at_epoch=int(d["updated_at_epoch"]),
        version=int(d["version"]),
        status=d["status"],
        nested_objects=[_to_nested_obj(x) for x in d.get("nested_objects", [])],
    )


@strawberry.type
class BenchmarkNested2Strawberry:
    id: uuid.UUID
    metric_name: str
    metric_value: int
    is_active: bool
    created_at: datetime.datetime


@strawberry.type
class BenchmarkNestedStrawberry:
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
    nested2_objects: List[BenchmarkNested2Strawberry]


@strawberry.type
class BenchmarkRootStrawberry:
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
    nested_objects: List[BenchmarkNestedStrawberry]
