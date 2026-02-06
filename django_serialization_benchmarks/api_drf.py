from typing import List, Dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from drf_pydantic import DrfPydanticSerializer
from .types_pydantic import BenchmarkRootPydantic, load_pydantic_data

# Cache for memoization
_drf_cache: Dict[str, List[BenchmarkRootPydantic]] = {}


class BenchmarkNested2Serializer(serializers.Serializer):
    id = serializers.UUIDField()
    metricName = serializers.CharField(source="metric_name")
    metricValue = serializers.IntegerField(source="metric_value")
    isActive = serializers.BooleanField(source="is_active")
    createdAt = serializers.DateTimeField(source="created_at")


class BenchmarkNestedSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    label = serializers.CharField()
    value = serializers.IntegerField()
    isInternal = serializers.BooleanField(source="is_internal")
    score = serializers.FloatField()
    notes = serializers.CharField()
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    priority = serializers.IntegerField()
    categoryCode = serializers.CharField(source="category_code")
    nested2Objects = BenchmarkNested2Serializer(source="nested2_objects", many=True)


class BenchmarkRootSerializer(DrfPydanticSerializer):
    """
    Using DrfPydanticSerializer as base, but manually defining fields
    due to automatic discovery issues with Pydantic v2 in this environment.
    """

    id = serializers.UUIDField()
    index = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    owner = serializers.CharField()
    createdAtEpoch = serializers.IntegerField(source="created_at_epoch")
    updatedAtEpoch = serializers.IntegerField(source="updated_at_epoch")
    version = serializers.IntegerField()
    status = serializers.CharField()
    nestedObjects = BenchmarkNestedSerializer(source="nested_objects", many=True)


class DRFJsonBenchmarkView(APIView):
    @extend_schema(responses={200: BenchmarkRootPydantic})
    def get(self, request: Request, filename: str) -> Response:
        data = load_pydantic_data(filename)

        # Use Pydantic's model_dump with by_alias=True
        return Response([item.model_dump(by_alias=True) for item in data])


class DRFPydanticBenchmarkView(APIView):
    @extend_schema(responses={200: BenchmarkRootSerializer(many=True)})
    def get(self, request: Request, filename: str) -> Response:
        data = load_pydantic_data(filename)

        # Use the serializer that inherits from DrfPydanticSerializer
        serializer = BenchmarkRootSerializer(data, many=True)
        return Response(serializer.data)
