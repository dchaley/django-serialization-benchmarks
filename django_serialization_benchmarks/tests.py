import json
from django.test import TestCase, Client
from django.urls import reverse

class EndpointConsistencyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.filename = "benchmark_data_10_5_5.json"

    def test_endpoints_return_camel_case(self):
        endpoints = [
            "/api/ninja-benchmark/" + self.filename,
            reverse("drf_pydantic", kwargs={"filename": self.filename}),
            reverse("drf_json", kwargs={"filename": self.filename}),
            reverse("drf_pydantic_model_dump_renderer", kwargs={"filename": self.filename}),
            reverse("drf_pydantic_json_renderer", kwargs={"filename": self.filename}),
            reverse("pydantic_http_response", kwargs={"filename": self.filename}),
        ]

        for url in endpoints:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIsInstance(data, list)
                if len(data) > 0:
                    first_item = data[0]
                    # Check for camelCase keys
                    self.assertIn("nestedObjects", first_item, f"Expected camelCase in {url}")
                    self.assertNotIn("nested_objects", first_item, f"Did not expect snake_case in {url}")

    def test_strawberry_camel_case(self):
        url = "/graphql/"
        query = """
        query ($filename: String!) {
          benchmarkVanillaTypes(filename: $filename) {
            id
            index
            name
            nestedObjects {
              id
              label
              nested2Objects {
                id
                metricName
              }
            }
          }
        }
        """
        response = self.client.post(
            url,
            data=json.dumps({"query": query, "variables": {"filename": self.filename}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn("errors", data)
        # Strawberry should already be camelCase
        self.assertIn("nestedObjects", data["data"]["benchmarkVanillaTypes"][0])

    def test_data_consistency(self):
        # Queries for all variants
        filename = self.filename
        
        # 1. Ninja
        ninja_res = self.client.get(f"/api/ninja-benchmark/{filename}").json()
        
        # 2. DRF Pydantic
        drf_pydantic_res = self.client.get(reverse("drf_pydantic", kwargs={"filename": filename})).json()
        
        # 3. DRF JSON
        drf_json_res = self.client.get(reverse("drf_json", kwargs={"filename": filename})).json()

        # 4. DRF Model Dump Renderer
        drf_model_dump_renderer_res = self.client.get(reverse("drf_pydantic_model_dump_renderer", kwargs={"filename": filename})).json()

        # 5. DRF JSON Renderer
        drf_json_renderer_res = self.client.get(reverse("drf_pydantic_json_renderer", kwargs={"filename": filename})).json()

        # 6. Pydantic HttpResponse (Vanilla Django)
        pydantic_http_response_res = self.client.get(reverse("pydantic_http_response", kwargs={"filename": filename})).json()

        # 7. Strawberry Vanilla
        query_vanilla = """
        query ($filename: String!) {
          benchmarkVanillaTypes(filename: $filename) {
            id index name description category owner createdAtEpoch updatedAtEpoch version status
            nestedObjects {
              id label value isInternal score notes createdAt updatedAt priority categoryCode
              nested2Objects { id metricName metricValue isActive createdAt }
            }
          }
        }
        """
        strawberry_vanilla_res = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query_vanilla, "variables": {"filename": filename}}),
            content_type="application/json"
        ).json()["data"]["benchmarkVanillaTypes"]

        # 5. Strawberry Pydantic
        query_pydantic = """
        query ($filename: String!) {
          benchmarkPydanticTypes(filename: $filename) {
            id index name description category owner createdAtEpoch updatedAtEpoch version status
            nestedObjects {
              id label value isInternal score notes createdAt updatedAt priority categoryCode
              nested2Objects { id metricName metricValue isActive createdAt }
            }
          }
        }
        """
        strawberry_pydantic_res = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query_pydantic, "variables": {"filename": filename}}),
            content_type="application/json"
        ).json()["data"]["benchmarkPydanticTypes"]

        all_results = [
            ("Ninja", ninja_res),
            ("DRF Pydantic", drf_pydantic_res),
            ("DRF JSON", drf_json_res),
            ("DRF Model Dump Renderer", drf_model_dump_renderer_res),
            ("DRF JSON Renderer", drf_json_renderer_res),
            ("Pydantic HttpResponse", pydantic_http_response_res),
            ("Strawberry Vanilla", strawberry_vanilla_res),
            ("Strawberry Pydantic", strawberry_pydantic_res),
        ]

        def normalize(data):
            if isinstance(data, list):
                return [normalize(i) for i in data]
            if isinstance(data, dict):
                new_dict = {}
                for k, v in data.items():
                    # Normalize dates - some might be Z, some +00:00, some have more microsecond precision
                    if k in ["createdAt", "updatedAt"] and isinstance(v, str):
                        # Use isoformat normalization
                        import datetime
                        try:
                            dt = datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
                            # Normalize to seconds precision or fixed microseconds to match
                            v = dt.strftime("%Y-%m-%dT%H:%M:%S")
                        except ValueError:
                            pass
                    new_dict[k] = normalize(v)
                return new_dict
            return data

        normalized_results = [(name, normalize(res)) for name, res in all_results]
        
        reference_name, reference_data = normalized_results[0]
        for name, data in normalized_results[1:]:
            self.assertEqual(len(data), len(reference_data), f"{name} length mismatch")
            for i in range(len(data)):
                self.assertEqual(data[i], reference_data[i], f"{name} mismatch at index {i} compared to {reference_name}")
