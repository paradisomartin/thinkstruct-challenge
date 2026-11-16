import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import connection
from django.test import TestCase

from patents.models import Patent
from patents.services.indexing import rebuild_search_index
from patents.services.ingestion import ingest_directory
from patents.services.search import SearchInputError, search_patents


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


class SearchRankingRegressionTests(TestCase):
    def ingest(self, rows):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "fixture.json").write_text(json.dumps(rows), encoding="utf-8")
            ingest_directory(path)
        rebuild_search_index()

    def direct_ranks(self, query):
        """Independent reference: no Django SearchRank expression."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT doc_number,
                       ts_rank(search_vector, plainto_tsquery('english', %s)) AS score
                FROM patents_patent
                WHERE search_vector @@ plainto_tsquery('english', %s)
                ORDER BY score DESC, doc_number
            """, [query, query])
            return cursor.fetchall()

    def test_weights_affect_scores_not_just_document_order(self):
        self.ingest([
            {"doc_number": "001", "detailed_description": ["Wheel"]},
            {"doc_number": "002", "claims": ["Wheel"]},
            {"doc_number": "003", "abstract": "Wheel"},
            {"doc_number": "004", "title": "Wheel"},
        ])
        rows = search_patents(query="wheel")["results"]
        scores = {row["doc_number"]: row["score"] for row in rows}
        self.assertGreater(scores["004"], scores["003"])
        self.assertEqual(scores["003"], scores["002"])
        self.assertGreater(scores["002"], scores["001"])
        self.assertEqual([row["doc_number"] for row in rows], ["004", "002", "003", "001"])

    def test_service_scores_match_direct_sql_for_single_and_multiple_terms(self):
        self.ingest([
            {"doc_number": "001", "title": "Wheel", "claims": ["Rotating spoke"]},
            {"doc_number": "002", "abstract": "Wheel spoke"},
            {"doc_number": "003", "detailed_description": ["Wheel wheel spoke"]},
        ])
        for query in ("wheel", "wheel spoke", "rotating"):
            with self.subTest(query=query):
                expected = self.direct_ranks(query)
                actual = search_patents(query=query)["results"]
                self.assertEqual([row["doc_number"] for row in actual], [pk for pk, _ in expected])
                for row, (_, score) in zip(actual, expected):
                    self.assertAlmostEqual(row["score"], score, places=7)

    def test_excerpt_uses_original_term_frequency_not_serialized_vector_text(self):
        self.ingest([{
            "doc_number": "001",
            "claims": ["Wheel", "  Wheel wheel wheel wheel.  "],
        }])
        row = search_patents(query="wheel")["results"][0]
        self.assertEqual(row["excerpt"], {
            "text": "  Wheel wheel wheel wheel.  ",
            "source_field": "claims", "source_index": 1,
        })
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT source_index
                FROM patents_passage
                WHERE patent_id = '001'
                ORDER BY ts_rank(to_tsvector('english', text),
                                 plainto_tsquery('english', 'wheel')) DESC, source_index
                LIMIT 1
            """)
            self.assertEqual(row["excerpt"]["source_index"], cursor.fetchone()[0])

    def test_real_ties_have_stable_pages_without_duplicates(self):
        self.ingest([
            {"doc_number": pk, "title": "Wheel"} for pk in ("003", "001", "002")
        ])
        pages = [search_patents(query="wheel", limit=1, offset=i) for i in range(4)]
        self.assertEqual([page["total_matches"] for page in pages], [3, 3, 3, 3])
        rows = [row for page in pages for row in page["results"]]
        self.assertEqual([row["doc_number"] for row in rows], ["001", "002", "003"])
        self.assertEqual(len({row["score"] for row in rows}), 1)
        self.assertEqual(pages[-1]["results"], [])

    def test_claim_only_and_description_only_patents_remain_searchable(self):
        self.ingest([
            {"doc_number": "001", "claims": ["A flexible spoke"]},
            {"doc_number": "002", "detailed_description": ["A flexible spoke"]},
        ])
        response = search_patents(query="flexible spoke")
        self.assertEqual(response["total_matches"], 2)
        rows = {row["doc_number"]: row for row in response["results"]}
        for pk, field in (("001", "claims"), ("002", "detailed_description")):
            self.assertIsNone(rows[pk]["title"])
            self.assertIsNone(rows[pk]["abstract"])
            self.assertEqual(rows[pk]["excerpt"]["source_field"], field)
            self.assertEqual(rows[pk]["excerpt"]["source_index"], 0)

    def test_excerpt_ties_keep_original_index_and_claims_precede_descriptions(self):
        self.ingest([{
            "doc_number": "001",
            "claims": ["", "Wheel", "Wheel"],
            "detailed_description": ["Wheel wheel wheel wheel"],
        }])
        excerpt = search_patents(query="wheel")["results"][0]["excerpt"]
        self.assertEqual(excerpt, {
            "text": "Wheel", "source_field": "claims", "source_index": 1,
        })

    def test_search_does_not_depend_on_database_default_language(self):
        self.ingest([{"doc_number": "001", "claims": ["Rotating wheels"]}])
        expected = search_patents(query="rotate wheel")
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL default_text_search_config = 'pg_catalog.simple'")
        self.assertEqual(search_patents(query="rotate wheel"), expected)

    def test_punctuation_only_and_stop_words_reject_even_with_filter(self):
        for query in ("!!!", "---", "the and of", "' | &"):
            with self.subTest(query=query), self.assertRaisesRegex(SearchInputError, "no searchable"):
                search_patents(query=query, classification_prefix="B60B")

    def test_apostrophes_hyphens_repetition_and_operators_follow_plain_sql(self):
        self.ingest([
            {"doc_number": "001", "title": "Driver's wheel-spoke assembly"},
            {"doc_number": "002", "claims": ["Wheel", "Spoke"]},
            {"doc_number": "003", "abstract": "Pneumatic tire"},
        ])
        for query in (
            "driver's", "wheel-spoke", "wheel wheel", "wheel & spoke",
            "wheel | nonexistentlexeme", "wheel !spoke", "'wheel'",
        ):
            with self.subTest(query=query):
                expected = self.direct_ranks(query)
                actual = search_patents(query=query)["results"]
                self.assertEqual([row["doc_number"] for row in actual], [pk for pk, _ in expected])
                for row, (_, score) in zip(actual, expected):
                    self.assertAlmostEqual(row["score"], score, places=7)
