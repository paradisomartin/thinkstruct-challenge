import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.management import call_command
from django.db import connection
from django.test import TestCase

from patents.models import Patent
from patents.services.indexing import rebuild_search_index
from patents.services.ingestion import ingest_directory


class SearchIndexTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def ingest(self, rows):
        (self.directory / "patents.json").write_text(json.dumps(rows), encoding="utf-8")
        return ingest_directory(self.directory)

    def matches(self, text):
        query = SearchQuery(text, config="english", search_type="plain")
        return list(
            Patent.objects.filter(search_vector=query)
            .annotate(rank=SearchRank("search_vector", query))
            .order_by("-rank", "doc_number")
            .values_list("doc_number", flat=True)
        )

    def test_terms_match_across_fields_and_stemming(self):
        self.ingest([{
            "doc_number": "001", "title": "Wheels", "abstract": "Flexible",
            "claims": ["A spoke"], "detailed_description": ["Rotating assembly"],
        }])
        self.assertEqual(rebuild_search_index()["indexed"], 1)
        self.assertEqual(self.matches("wheel flexible spoke rotate"), ["001"])
        self.assertEqual(self.matches("wheel absent"), [])

    def test_native_weights_order_title_abstract_claim_description(self):
        self.ingest([
            {"doc_number": "004", "detailed_description": ["Wheel"]},
            {"doc_number": "003", "claims": ["Wheel"]},
            {"doc_number": "002", "abstract": "Wheel"},
            {"doc_number": "001", "title": "Wheel"},
        ])
        rebuild_search_index()
        self.assertEqual(self.matches("wheel"), ["001", "002", "003", "004"])

    def test_only_normalized_passages_are_indexed(self):
        self.ingest([{
            "doc_number": "001", "abstract": "Wheel",
            "claims": ["", "1 . (canceled)", "A spoke"],
            "detailed_description": [""],
        }])
        rebuild_search_index()
        self.assertEqual(self.matches("spoke"), ["001"])
        self.assertEqual(self.matches("canceled"), [])
        self.assertEqual(self.matches("wheel"), ["001"])

    def test_ingestion_requires_explicit_rebuild_and_rerun_is_stable(self):
        rows = [{"doc_number": "001", "title": "Wheel"}]
        self.ingest(rows)
        self.assertIsNone(Patent.objects.get().search_vector)
        self.assertEqual(self.matches("wheel"), [])
        rebuild_search_index()
        first = Patent.objects.get().search_vector
        self.ingest(rows)
        self.assertEqual(Patent.objects.get().search_vector, first)
        self.ingest(rows + [{"doc_number": "002", "title": "Spoke"}])
        self.assertEqual(self.matches("spoke"), [])
        rebuild_search_index()
        self.assertEqual(self.matches("spoke"), ["002"])
        self.assertEqual(Patent.objects.get(pk="001").search_vector, first)
        rebuild_search_index()
        self.assertEqual(Patent.objects.get(pk="001").search_vector, first)

    def test_empty_rebuild_command_outputs_json(self):
        output = StringIO()
        call_command("rebuild_search_index", stdout=output)
        self.assertEqual(json.loads(output.getvalue())["indexed"], 0)

    def test_gin_index_exists(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT indexdef FROM pg_indexes WHERE schemaname = current_schema() "
                "AND tablename = 'patents_patent' AND indexname = 'patent_search_vector_gin'"
            )
            self.assertIn("USING gin (search_vector)", cursor.fetchone()[0])
