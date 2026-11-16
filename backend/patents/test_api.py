import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase

from patents.services.indexing import rebuild_search_index
from patents.services.ingestion import ingest_directory


class SearchAPITests(TestCase):
    url = "/api/patents/search"

    def setUp(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "sample.json").write_text(json.dumps([
                {
                    "doc_number": "001", "title": "Wheel assembly",
                    "abstract": "Flexible spokes", "classification": "B60B104FI",
                    "claims": ["", "  A rotating spoke.  "],
                },
                {
                    "doc_number": "002", "title": "Wheel assembly",
                    "abstract": "Flexible spokes", "classification": "B60C100FI",
                },
            ]), encoding="utf-8")
            ingest_directory(path)
        rebuild_search_index()

    def test_ranked_response_serializes_provenance(self):
        response = self.client.get(self.url, {
            "query": "wheel spoke", "classification_prefix": "B60B", "limit": 1,
        })
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_matches"], 1)
        row = body["results"][0]
        self.assertEqual(row["doc_number"], "001")
        self.assertIsInstance(row["score"], float)
        self.assertEqual(row["excerpt"], {
            "text": "  A rotating spoke.  ", "source_field": "claims", "source_index": 1,
        })
        self.assertEqual(row["source_file"], "sample.json")
        self.assertEqual(row["record_index"], 0)
        self.assertIsNone(row["bibtex"])
        self.assertNotIn("raw_record", row)
        self.assertNotIn("search_vector", row)

    def test_repeated_keyword_parameters_and_combined_filters(self):
        response = self.client.get(
            self.url + "?query=wheel&classification_prefix=B60B"
            "&title_keywords=wheel&title_keywords=assembly"
            "&abstract_keywords=flexible&abstract_keywords=spokes",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_matches"], 1)
        self.assertEqual(body["results"][0]["doc_number"], "001")
        self.assertEqual(body["effective_request"]["title_keywords"], ["wheel", "assembly"])
        response = self.client.get(self.url + "?title_keywords=wheel&title_keywords=absent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_matches"], 0)

    def test_title_lookup_and_pagination(self):
        response = self.client.get(self.url, {
            "title_exact": " WHEEL   assembly ", "limit": 1, "offset": 1,
        })
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_matches"], 2)
        self.assertEqual(body["results"][0]["doc_number"], "002")
        self.assertIsNone(body["results"][0]["score"])
        self.assertEqual(body["effective_request"]["title_exact"], "wheel assembly")

    def test_invalid_domain_and_transport_inputs(self):
        for params in (
            {}, {"query": "the and of"}, {"query": "wheel", "limit": 0},
            {"query": "wheel", "limit": 101}, {"query": "wheel", "limit": "oops"},
            {"query": "wheel", "offset": -1}, {"query": "wheel", "offset": "oops"},
            {"title_keywords": "two words"}, {"classification_prefix": "B60%"},
        ):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, 422)
                self.assertIn("detail", response.json())

    def test_no_matches_is_success(self):
        response = self.client.get(self.url, {"query": "nonexistentlexeme"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
        self.assertEqual(response.json()["total_matches"], 0)

    def test_database_failure_is_sanitized(self):
        with patch("patents.api.search_patents", side_effect=OperationalError("private details")):
            with self.assertLogs("thinkstruct.search", level="WARNING") as captured:
                response = self.client.get(self.url, {"query": "wheel"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Search temporarily unavailable"})
        self.assertNotIn("private details", response.content.decode())
        self.assertNotIn("private details", "\n".join(captured.output))

    def test_openapi_documents_filters_and_responses(self):
        schema = self.client.get("/api/openapi.json").json()
        operation = schema["paths"][self.url]["get"]
        self.assertTrue({"200", "422", "503"}.issubset(operation["responses"]))
        params = {item["name"]: item for item in operation["parameters"]}
        self.assertEqual(params["title_keywords"]["schema"]["type"], "array")
        self.assertEqual(params["abstract_keywords"]["in"], "query")
        self.assertEqual(params["limit"]["schema"]["maximum"], 100)
