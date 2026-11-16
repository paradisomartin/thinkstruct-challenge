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
from patents.services.search import SearchInputError, search_patents


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


class SearchServiceTests(TestCase):
    def setUp(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "sample.json").write_text(json.dumps([
                {
                    "doc_number": "001", "title": "Wheel assembly",
                    "abstract": "Flexible spokes support rotation.",
                    "classification": "B60B104FI", "filename": "original.XML",
                    "claims": ["1 . (canceled)", "  A rotating spoke.  "],
                    "detailed_description": ["", "The wheel rotates."],
                },
                {
                    "doc_number": "002", "title": "Wheel assembly",
                    "abstract": "Flexible spokes support rotation.",
                    "classification": "B60C100FI",
                },
                {
                    "doc_number": "003", "title": "Wheels assembly",
                    "abstract": "A pneumatic tyre.", "classification": "B60B200FI",
                },
                {
                    "doc_number": "004", "abstract": "Wheel assembly",
                    "classification": "B60B200FI",
                },
                {
                    "doc_number": "005", "title": "  STRAẞE\n  ÉLECTRIQUE ",
                    "abstract": "A street vehicle.", "classification": "B60R",
                },
            ]), encoding="utf-8")
            ingest_directory(path)
        rebuild_search_index()

    def ids(self, response):
        return [row["doc_number"] for row in response["results"]]

    def test_rank_ties_pagination_and_total(self):
        response = search_patents(query="wheel", limit=2)
        self.assertEqual(self.ids(response), ["001", "002"])
        self.assertEqual(response["total_matches"], 4)
        self.assertGreater(response["results"][0]["score"], 0)
        self.assertEqual(response["results"][0]["ranking_method"], "ts_rank")
        second = search_patents(query="wheel", limit=2, offset=2)
        self.assertEqual(self.ids(second), ["003", "004"])
        self.assertEqual(second["total_matches"], 4)
        self.assertEqual(search_patents(query="wheel", offset=99)["total_matches"], 4)

    def test_all_filters_apply_before_pagination(self):
        response = search_patents(
            query="wheel", classification_prefix="B60B",
            title_keywords=["wheel"], abstract_keywords=["flexible", "spokes"],
            title_exact=" WHEEL   assembly ", limit=1,
        )
        self.assertEqual(self.ids(response), ["001"])
        self.assertEqual(response["total_matches"], 1)
        self.assertEqual(response["effective_request"]["title_exact"], "wheel assembly")
        self.assertEqual(search_patents(
            query="wheel", classification_prefix="B60C",
        )["total_matches"], 1)

    def test_literal_tokens_do_not_stem_or_match_substrings(self):
        self.assertEqual(self.ids(search_patents(title_keywords=["wheel"])), ["001", "002"])
        self.assertEqual(self.ids(search_patents(title_keywords=["wheels"])), ["003"])
        self.assertEqual(self.ids(search_patents(title_keywords=["whee"])), [])
        self.assertEqual(self.ids(search_patents(abstract_keywords=["spoke"])), [])
        self.assertEqual(
            self.ids(search_patents(title_keywords=["STRASSE", "électrique"])), ["005"],
        )
        self.assertEqual(self.ids(search_patents(
            title_exact="strasse électrique",
        )), ["005"])

    def test_filter_only_order_score_and_metadata_evidence(self):
        response = search_patents(classification_prefix="B60B")
        self.assertEqual(self.ids(response), ["001", "003", "004"])
        for row in response["results"]:
            self.assertIsNone(row["score"])
            self.assertIsNone(row["excerpt"])
        response = search_patents(title_exact="Wheel assembly")
        self.assertEqual(self.ids(response), ["001", "002"])
        self.assertEqual(response["results"][0]["excerpt"], {
            "text": "Wheel assembly", "source_field": "title", "source_index": None,
        })
        response = search_patents(abstract_keywords=["pneumatic"])
        self.assertEqual(response["results"][0]["excerpt"]["source_field"], "abstract")

    def test_cross_field_query_prefers_original_claim_evidence(self):
        response = search_patents(query="wheel flexible spoke", classification_prefix="B60B")
        self.assertEqual(self.ids(response), ["001"])
        row = response["results"][0]
        self.assertEqual(row["excerpt"], {
            "text": "  A rotating spoke.  ", "source_field": "claims", "source_index": 1,
        })
        self.assertEqual(row["source_file"], "sample.json")
        self.assertEqual(row["record_index"], 0)
        self.assertEqual(row["filename"], "original.XML")
        self.assertIsNone(row["bibtex"])

    def test_description_then_scalar_fallback(self):
        response = search_patents(query="wheel", classification_prefix="B60B")
        self.assertEqual(response["results"][0]["excerpt"], {
            "text": "The wheel rotates.",
            "source_field": "detailed_description", "source_index": 1,
        })
        row = search_patents(query="pneumatic")["results"][0]
        self.assertEqual(row["excerpt"]["source_field"], "abstract")
        row = search_patents(query="wheel", classification_prefix="B60C")["results"][0]
        self.assertEqual(row["excerpt"]["source_field"], "title")

    def test_no_matches(self):
        response = search_patents(query="nonexistentlexeme")
        self.assertEqual(response["results"], [])
        self.assertEqual(response["total_matches"], 0)

    def test_stop_word_query_rejected_even_with_filter(self):
        with self.assertRaisesRegex(SearchInputError, "no searchable"):
            search_patents(query="the and of", classification_prefix="B60B")

    def test_invalid_inputs(self):
        for arguments in (
            {}, {"query": " "}, {"title_keywords": []},
            {"title_keywords": [""]}, {"title_keywords": ["two words"]},
            {"title_keywords": "wheel"}, {"abstract_keywords": [123]},
            {"classification_prefix": "B60%"}, {"classification_prefix": "b60b"},
            {"query": 123}, {"title_exact": []},
            {"query": "wheel", "limit": 0}, {"query": "wheel", "limit": 101},
            {"query": "wheel", "limit": True}, {"query": "wheel", "offset": -1},
            {"query": "wheel", "offset": 1.5},
        ):
            with self.subTest(arguments=arguments), self.assertRaises(SearchInputError):
                search_patents(**arguments)

    def test_plain_query_does_not_accept_raw_operators(self):
        self.assertEqual(
            self.ids(search_patents(query="wheel | nonexistentlexeme")), [],
        )
