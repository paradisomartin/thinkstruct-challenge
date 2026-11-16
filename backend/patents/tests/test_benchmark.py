import json
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from patents.models import Patent
from patents.services.benchmark import benchmark_search, summarize
from patents.services.indexing import rebuild_search_index


class BenchmarkTests(TestCase):
    def test_aggregation_uses_median_and_nearest_rank(self):
        result = summarize(list(range(1, 21)))
        self.assertEqual(result["p50_ms"], 10.5)
        self.assertEqual(result["p95_ms"], 19)
        self.assertEqual(len(result["samples_ms"]), 20)

    def test_requires_data_and_complete_index(self):
        with self.assertRaisesRegex(ValueError, "rebuild"):
            benchmark_search()
        self.patent()
        with self.assertRaisesRegex(ValueError, "rebuild"):
            benchmark_search()

    def patent(self):
        Patent.objects.create(
            doc_number="001", title="Wheel spoke pneumatic tire pressure",
            abstract="Wheel pressure", classification="B60B",
            source_file="fixture.json", record_index=0, content_sha256="a" * 64,
            raw_record={},
        )

    def test_command_report_has_samples_and_does_not_modify_patents(self):
        self.patent()
        rebuild_search_index()
        original = Patent.objects.get().search_vector
        output = StringIO()
        call_command("benchmark_search", repetitions=2, warmups=1, limit=1, stdout=output)
        report = json.loads(output.getvalue())
        self.assertEqual(report["dataset"]["patents"], 1)
        self.assertEqual(len(report["scenarios"]), 4)
        for scenario in report["scenarios"]:
            for variant in scenario["variants"].values():
                self.assertEqual(len(variant["samples_ms"]), 2)
                self.assertEqual(len(variant["response_sha256"]), 64)
        self.assertEqual(Patent.objects.get().search_vector, original)
        self.assertEqual(Patent.objects.count(), 1)

    def test_invalid_parameters_and_unstable_responses_fail(self):
        for kwargs in ({"repetitions": 0}, {"warmups": 0}, {"limit": 101}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                benchmark_search(**kwargs)
        self.patent()
        rebuild_search_index()
        with patch("patents.services.benchmark.search_patents", side_effect=[
            {"total_matches": 1}, {"total_matches": 1}, {"total_matches": 2},
        ]):
            with self.assertRaisesRegex(ValueError, "Results changed"):
                benchmark_search(repetitions=1, warmups=1)
        with self.assertRaises(CommandError):
            call_command("benchmark_search", repetitions=0, stdout=StringIO())
