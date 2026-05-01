"""
URL configuration for django_serialization_benchmarks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView
from .api_strawberry import schema
from .api_ninja import api
from .api_drf import (
    DRFPydanticBenchmarkView,
    DRFJsonBenchmarkView,
    DRFPydanticModelDumpRendererView,
    DRFPydanticJSONRendererView,
    pydantic_http_response_benchmark_view,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema))),
    path("api/", api.urls),
    path(
        "api/drf-pydantic-benchmark/<str:filename>",
        DRFPydanticBenchmarkView.as_view(),
        name="drf_pydantic",
    ),
    path(
        "api/drf-json-benchmark/<str:filename>",
        DRFJsonBenchmarkView.as_view(),
        name="drf_json",
    ),
    path(
        "api/drf-pydantic-model-dump-renderer-benchmark/<str:filename>",
        DRFPydanticModelDumpRendererView.as_view(),
        name="drf_pydantic_model_dump_renderer",
    ),
    path(
        "api/drf-pydantic-json-renderer-benchmark/<str:filename>",
        DRFPydanticJSONRendererView.as_view(),
        name="drf_pydantic_json_renderer",
    ),
    path(
        "api/pydantic-http-response-benchmark/<str:filename>",
        pydantic_http_response_benchmark_view,
        name="pydantic_http_response",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
