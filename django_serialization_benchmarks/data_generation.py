import datetime
import json
import random
import string
import time
import uuid
from pathlib import Path
from typing import List


def _rand_str(n: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def _mk_nested2(z: int) -> List[dict]:
    now = datetime.datetime.now(datetime.timezone.utc)
    return [
        {
            "id": str(uuid.uuid4()),
            "metric_name": _rand_str(8),
            "metric_value": random.randint(0, 10_000),
            "is_active": random.choice([True, False]),
            "created_at": (
                now - datetime.timedelta(days=random.randint(0, 100))
            ).isoformat(),
        }
        for _ in range(z)
    ]


def _mk_nested(y: int, z: int) -> List[dict]:
    now = datetime.datetime.now(datetime.timezone.utc)
    return [
        {
            "id": str(uuid.uuid4()),
            "label": _rand_str(12),
            "value": random.randint(0, 1_000_000),
            "is_internal": random.choice([True, False]),
            "score": random.uniform(0, 100),
            "notes": _rand_str(50),
            "created_at": (
                now - datetime.timedelta(days=random.randint(101, 200))
            ).isoformat(),
            "updated_at": (
                now - datetime.timedelta(days=random.randint(0, 100))
            ).isoformat(),
            "priority": random.randint(1, 10),
            "category_code": _rand_str(4).upper(),
            "nested2_objects": _mk_nested2(z),
        }
        for _ in range(y)
    ]


def generate_benchmark_json(
    num_rows: int,
    num_nested_objs: int,
    num_nested2_objs: int,
    out_path: str = "benchmark_data.json",
):
    """
    Generate X root objects, each with Y nested objects, each with Z subnested objects.
    Writes JSON to out_path and returns the absolute path.
    """
    now = int(time.time())
    data = []
    for i in range(num_rows):
        root = {
            "id": str(uuid.uuid4()),
            "index": i,
            "name": _rand_str(16),
            "description": _rand_str(40),
            "category": random.choice(["alpha", "beta", "gamma", "delta"]),
            "owner": random.choice(["alice", "bob", "carol", "dave"]),
            "created_at_epoch": now - random.randint(0, 1_000_000),
            "updated_at_epoch": now,
            "version": random.randint(1, 20),
            "status": random.choice(["active", "paused", "archived"]),
            "nested_objects": _mk_nested(num_nested_objs, num_nested2_objs),
        }
        data.append(root)

    # Write JSON to out_path
    Path(out_path).write_text(json.dumps(data), encoding="utf-8")
