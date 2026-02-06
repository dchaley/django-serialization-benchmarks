import json
from typing import List, Dict
from ninja import NinjaAPI
from .types_pydantic import BenchmarkRootPydantic, load_pydantic_data

api = NinjaAPI()


@api.get("/ninja-benchmark/{filename}", response=List[BenchmarkRootPydantic], url_name="ninja_pydantic", by_alias=True)
def ninja_pydantic(request, filename: str) -> List[BenchmarkRootPydantic]:
    data = load_pydantic_data(filename)
    return data
