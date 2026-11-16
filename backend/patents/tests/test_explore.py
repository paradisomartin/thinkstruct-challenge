from concurrent.futures import ThreadPoolExecutor
from datetime import date
from unittest.mock import patch

from django.db import connection, connections, transaction
from django.test import TransactionTestCase

from patents.models import Patent
from patents.services.explore import explore_patents, source_week
from patents.services.indexing import rebuild_search_index
from patents.services.search import SearchInputError, render_search, search_patents


class ExploreTests(TransactionTestCase):
    def setUp(self):
        rows = [
            ("001", "Wheel assembly", "Flexible spokes", "B60B104FI", "patents_ipa240215.json"),
            ("002", "Wheel assembly", "Pressure sensor", "B60C100FI", "patents_ipa240222.json"),
            ("003", "Brake actuator", "Safety", "B60D101FI", "patents_ipa240222.json"),
            ("004", "Wheel assembly", "Flexible spokes", None, "unknown.json"),
            ("005", "Wheel assembly", "Flexible spokes", "?", "patents_ipa240230.json"),
            ("006", "Wheel assembly", "Flexible spokes", "C10A100FI", "nested/patents_ipa240215.json"),
        ]
        Patent.objects.bulk_create([
            Patent(
                doc_number=pk, title=title, abstract=abstract, classification=code,
                source_file=source, record_index=0, content_sha256="a" * 64,
                raw_record={}, filename="US20240000001A1-20240229.XML",
            )
            for pk, title, abstract, code, source in rows
        ])
        rebuild_search_index()

    def assert_consistent(self, response):
        total = response["total_matches"]
        self.assertEqual(
            sum(bucket["count"] for bucket in response["classification_facets"])
            + response["unclassified_count"], total,
        )
        for bucket in response["classification_facets"]:
            self.assertEqual(sum(child["count"] for child in bucket["children"]), bucket["count"])
        self.assertEqual(
            sum(bucket["count"] for bucket in response["source_weeks"])
            + response["unknown_source_week_count"], total,
        )

    def test_browse_groups_all_candidates_before_paging(self):
        response = explore_patents(limit=1)
        self.assertEqual(response["total_matches"], 6)
        self.assertEqual(len(response["results"]), 1)
        self.assertEqual(response["results"][0]["source_week"], date(2024, 2, 15))
        self.assertIsNone(response["results"][0]["score"])
        self.assertEqual(response["classification_facets"], [
            {"prefix": "B60", "count": 3, "children": [
                {"prefix": "B60B", "count": 1}, {"prefix": "B60C", "count": 1},
                {"prefix": "B60D", "count": 1},
            ]},
            {"prefix": "C10", "count": 1, "children": [{"prefix": "C10A", "count": 1}]},
        ])
        self.assertEqual(response["source_weeks"], [
            {"source_week": date(2024, 2, 15), "count": 2},
            {"source_week": date(2024, 2, 22), "count": 2},
        ])
        self.assertEqual(response["unclassified_count"], 2)
        self.assertEqual(response["unknown_source_week_count"], 2)
        self.assert_consistent(response)

    def test_pagination_changes_only_results_not_counts(self):
        first = explore_patents(limit=2)
        second = explore_patents(limit=2, offset=2)
        beyond = explore_patents(offset=100)
        for field in ("classification_facets", "source_weeks", "total_matches"):
            self.assertEqual(first[field], second[field])
            self.assertEqual(first[field], beyond[field])
        self.assertFalse(
            {row["doc_number"] for row in first["results"]}
            & {row["doc_number"] for row in second["results"]}
        )
        self.assertEqual(beyond["results"], [])

    def test_all_filters_apply_to_every_view(self):
        response = explore_patents(
            query="wheel", classification_prefix="B60", title_keywords=["assembly"],
            abstract_keywords=["pressure"], title_exact=" WHEEL  assembly ",
            source_week_from="2024-02-22", source_week_to="2024-02-22",
        )
        self.assertEqual([row["doc_number"] for row in response["results"]], ["002"])
        self.assertEqual(response["effective_request"]["title_exact"], "wheel assembly")
        self.assertEqual(response["effective_request"]["source_week_from"], date(2024, 2, 22))
        self.assert_consistent(response)

    def test_inclusive_date_bounds_and_unknown_dates(self):
        for filters, expected in [
            ({"source_week_from": "2024-02-15", "source_week_to": "2024-02-22"}, 4),
            ({"source_week_from": "2024-02-22"}, 2),
            ({"source_week_to": "2024-02-15"}, 2),
        ]:
            with self.subTest(filters=filters):
                response = explore_patents(**filters)
                self.assertEqual(response["total_matches"], expected)
                self.assertEqual(response["unknown_source_week_count"], 0)
                self.assert_consistent(response)

    def test_classification_drilldown_uses_filtered_counts(self):
        for prefix, expected in [("B60", 3), ("B60B", 1), ("B60B104", 1)]:
            response = explore_patents(classification_prefix=prefix)
            self.assertEqual(response["total_matches"], expected)
            self.assert_consistent(response)

    def test_search_ranking_and_evidence_are_reused_unchanged(self):
        expected = search_patents(query="wheel")
        response = explore_patents(query="wheel")
        for row in response["results"]:
            row.pop("source_week")
        self.assertEqual(response["results"], expected["results"])
        self.assertEqual(response["total_matches"], expected["total_matches"])

    def test_empty_results_and_empty_database_have_zero_counts(self):
        for response in [explore_patents(query="absent"), explore_patents(source_week_from="2030-01-01")]:
            self.assertEqual(response["results"], [])
            self.assertEqual(response["total_matches"], 0)
            self.assert_consistent(response)
        Patent.objects.all().delete()
        response = explore_patents()
        self.assertEqual(response["classification_facets"], [])
        self.assertEqual(response["source_weeks"], [])
        self.assert_consistent(response)

    def test_invalid_dates_and_existing_search_validation(self):
        for kwargs in [
            {"source_week_from": "2024-02-30"},
            {"source_week_to": "20240215"},
            {"source_week_from": 123},
            {"source_week_from": "2024-02-22", "source_week_to": "2024-02-15"},
            {"query": "the and of"}, {"limit": 0}, {"classification_prefix": "b60"},
        ]:
            with self.subTest(kwargs=kwargs), self.assertRaises(SearchInputError):
                explore_patents(**kwargs)

    def test_source_week_uses_only_valid_source_batch_filename(self):
        self.assertEqual(source_week("nested/patents_ipa240229.json"), date(2024, 2, 29))
        for name in ["patents_ipa230229.json", "patents_ipa241301.json", "other.json", "patents_ipa240215.json.bak"]:
            self.assertIsNone(source_week(name))

    def test_snapshot_survives_a_concurrent_metadata_update(self):
        def update_from_another_connection():
            try:
                Patent.objects.filter(pk="001").update(
                    title="Changed", classification="Z99Z", source_file="patents_ipa250101.json",
                )
            finally:
                connections["default"].close()

        def render_after_update(*args, **kwargs):
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_setting('transaction_isolation'), current_setting('transaction_read_only')")
                self.assertEqual(cursor.fetchone(), ("repeatable read", "on"))
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(update_from_another_connection).result(timeout=10)
            return render_search(*args, **kwargs)

        with patch("patents.services.explore.render_search", side_effect=render_after_update):
            response = explore_patents(classification_prefix="B60B")
        row = response["results"][0]
        self.assertEqual(row["title"], "Wheel assembly")
        self.assertEqual(row["classification"], "B60B104FI")
        self.assertEqual(row["source_week"], date(2024, 2, 15))
        self.assertEqual(Patent.objects.get(pk="001").title, "Changed")
        self.assert_consistent(response)

    def test_transaction_scope_is_not_nested_or_leaked(self):
        with transaction.atomic(), self.assertRaises(RuntimeError):
            explore_patents()
        with self.assertRaises(SearchInputError):
            explore_patents(query="the and of")
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_setting('transaction_read_only')")
            self.assertEqual(cursor.fetchone()[0], "off")
