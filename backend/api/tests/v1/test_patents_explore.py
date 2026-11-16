from unittest.mock import patch

from django.db import OperationalError
from django.test import TransactionTestCase

from patents.models import Patent
from patents.services.indexing import rebuild_search_index


class ExploreAPITests(TransactionTestCase):
    url = "/api/v1/patents/explore"

    def setUp(self):
        for pk, code, source in [
            ("001", "B60B104FI", "patents_ipa240215.json"),
            ("002", "B60C100FI", "patents_ipa240222.json"),
            ("003", None, "unknown.json"),
        ]:
            Patent.objects.create(
                doc_number=pk, title="Wheel assembly", abstract="Flexible spokes",
                classification=code, source_file=source, record_index=0,
                content_sha256="a" * 64, raw_record={},
            )
        rebuild_search_index()

    def test_browse_and_date_serialization(self):
        response = self.client.get(self.url, {"limit": 1})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_matches"], 3)
        self.assertEqual(len(body["results"]), 1)
        self.assertEqual(body["results"][0]["source_week"], "2024-02-15")
        self.assertEqual(body["source_weeks"], [
            {"source_week": "2024-02-15", "count": 1},
            {"source_week": "2024-02-22", "count": 1},
        ])
        self.assertEqual(body["unknown_source_week_count"], 1)
        self.assertEqual(body["unclassified_count"], 1)
        self.assertNotIn("raw_record", body["results"][0])
        self.assertNotIn("search_vector", body["results"][0])

    def test_combined_filters_repeated_parameters_and_inclusive_dates(self):
        response = self.client.get(
            self.url + "?query=wheel&classification_prefix=B60B"
            "&title_keywords=wheel&title_keywords=assembly"
            "&abstract_keywords=flexible&title_exact=Wheel%20assembly"
            "&source_week_from=2024-02-15&source_week_to=2024-02-15",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_matches"], 1)
        self.assertEqual(body["classification_facets"], [
            {"prefix": "B60", "count": 1, "children": [{"prefix": "B60B", "count": 1}]},
        ])
        self.assertEqual(body["effective_request"]["source_week_from"], "2024-02-15")
        self.assertEqual(body["effective_request"]["title_keywords"], ["wheel", "assembly"])

    def test_invalid_input_returns_422(self):
        for params in [
            {"source_week_from": "not-a-date"},
            {"source_week_to": "2024-02-30"},
            {"source_week_from": "2024-02-22", "source_week_to": "2024-02-15"},
            {"query": "the and of"}, {"limit": 101}, {"offset": -1},
            {"classification_prefix": "B60%"},
        ]:
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, 422)
                self.assertIn("detail", response.json())

    def test_database_failure_returns_sanitized_503(self):
        with patch("api.v1.patents.api.explore_patents", side_effect=OperationalError("private details")):
            with self.assertLogs("thinkstruct.search", level="WARNING") as captured:
                response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Search temporarily unavailable"})
        self.assertNotIn("private details", response.content.decode())
        self.assertNotIn("private details", "\n".join(captured.output))

    def test_schema_versions_routes_and_describes_explore(self):
        schema = self.client.get("/api/openapi.json").json()
        paths = schema["paths"]
        self.assertIn("/api/v1/patents/search", paths)
        self.assertNotIn("/api/patents/search", paths)
        operation = paths[self.url]["get"]
        self.assertTrue({"200", "422", "503"}.issubset(operation["responses"]))
        params = {item["name"]: item for item in operation["parameters"]}
        self.assertIn("source_week_from", params)
        self.assertIn("source_week_to", params)
        self.assertEqual(self.client.get("/api/patents/search", {"query": "wheel"}).status_code, 404)
