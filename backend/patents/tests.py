import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from .services.ingestion import IngestionError, ingest_directory, normalize_record
from .models import Passage, Patent


def record(doc_number="001"):
    return {
        "doc_number": doc_number,
        "title": "Wheel",
        "claims": ["1 - 5 . (canceled)", "  A wheel with a spoke.  "],
        "detailed_description": ["", "  ", "The spoke improves the wheel."],
    }


class IngestionTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def write(self, rows, filename="patents.json"):
        (self.directory / filename).write_text(json.dumps(rows), encoding="utf-8")

    def test_passages_preserve_original_text_and_positions(self):
        self.write([record()])
        result = ingest_directory(self.directory)
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["blank_entries"], 2)
        self.assertEqual(result["canceled_markers"], 1)
        self.assertEqual(
            Passage.objects.get(source_field="claims").text, "  A wheel with a spoke.  "
        )
        self.assertEqual(Passage.objects.get(source_field="claims").source_index, 1)
        self.assertEqual(Passage.objects.get(source_field="detailed_description").source_index, 2)
        patent = Patent.objects.get()
        self.assertEqual(patent.raw_record, record())
        self.assertEqual(patent.source_file, "patents.json")
        self.assertEqual(patent.record_index, 0)
        self.assertIsNone(patent.classification)

    def test_repeated_ingestion_is_idempotent(self):
        self.write([record()])
        ingest_directory(self.directory)
        result = ingest_directory(self.directory)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["unchanged"], 1)
        self.assertEqual(Patent.objects.count(), 1)
        self.assertEqual(Passage.objects.count(), 2)

    def test_keeps_patent_with_blank_only_description(self):
        raw = {"doc_number": "002", "abstract": "A useful wheel.", "detailed_description": [""]}
        self.write([raw])
        ingest_directory(self.directory)
        self.assertEqual(Patent.objects.count(), 1)
        self.assertEqual(Passage.objects.count(), 0)

    def test_cancellation_mentions_are_not_markers(self):
        raw = record()
        raw["claims"] = ["A controller that cancels wheel vibration."]
        metadata, passages, skipped = normalize_record(raw, "sample.json", 0)
        self.assertEqual(passages[0]["text"], raw["claims"][0])
        self.assertEqual(skipped["canceled_markers"], 0)

    def test_duplicate_ids_in_input_abort_without_writes(self):
        self.write([record()])
        self.write([record()], "second.json")
        with self.assertRaisesRegex(IngestionError, "duplicate"):
            ingest_directory(self.directory)
        self.assertEqual(Patent.objects.count(), 0)

    def test_database_conflict_rolls_back_new_records(self):
        self.write([record("002")])
        ingest_directory(self.directory)
        changed = record("002")
        changed["title"] = "Changed"
        self.write([record("001"), changed])
        with self.assertRaisesRegex(IngestionError, "Conflicting"):
            ingest_directory(self.directory)
        self.assertEqual(list(Patent.objects.values_list("doc_number", flat=True)), ["002"])
        self.assertEqual(Patent.objects.get().title, "Wheel")

    def test_invalid_json_in_later_file_aborts_without_writes(self):
        self.write([record()], "a.json")
        (self.directory / "z.json").write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(IngestionError, "invalid/unreadable JSON"):
            ingest_directory(self.directory)
        self.assertEqual(Patent.objects.count(), 0)

    def test_invalid_record_shapes_are_rejected(self):
        for invalid in ([], {"title": "No ID"}, {"doc_number": 1}, {"doc_number": " "},
                        {"doc_number": "001", "claims": "Wrong shape"},
                        {"doc_number": "001", "claims": [None]}):
            with self.subTest(raw=invalid), self.assertRaises(IngestionError):
                normalize_record(invalid, "sample.json", 0)

    def test_no_meaningful_text_is_rejected(self):
        with self.assertRaisesRegex(IngestionError, "no meaningful"):
            normalize_record(
                {"doc_number": "001", "claims": ["1 . (canceled)"],
                 "classification": "B60B"},
                "sample.json", 0,
            )

    def test_dry_run_does_not_write(self):
        self.write([record()])
        result = ingest_directory(self.directory, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["created"], 1)
        self.assertEqual(Patent.objects.count(), 0)

    def test_empty_directory_is_rejected(self):
        with self.assertRaisesRegex(IngestionError, "no JSON"):
            ingest_directory(self.directory)

    def test_changed_provenance_is_a_conflict(self):
        self.write([record()])
        ingest_directory(self.directory)
        original = self.directory / "patents.json"
        original.rename(self.directory / "renamed.json")
        with self.assertRaisesRegex(IngestionError, "Conflicting"):
            ingest_directory(self.directory)

    def test_logs_explain_stages_without_source_text(self):
        self.write([record()])
        with self.assertLogs("thinkstruct.ingestion", level="INFO") as captured:
            ingest_directory(self.directory)
        logs = "\n".join(captured.output)
        for stage in ("Ingestion started", "Source discovery completed",
                      "Input validation completed", "Database phase completed",
                      "Ingestion completed"):
            self.assertIn(stage, logs)
        self.assertNotIn("A wheel with a spoke.", logs)

    def test_command_stdout_remains_machine_readable(self):
        self.write([record()])
        output = StringIO()
        call_command("ingest_patents", str(self.directory), stdout=output)
        self.assertEqual(json.loads(output.getvalue())["created"], 1)

    def test_command_logs_failure_without_a_success_event(self):
        self.write([record(), record()])
        with self.assertLogs("thinkstruct.ingestion", level="INFO") as captured:
            with self.assertRaises(CommandError):
                call_command("ingest_patents", str(self.directory), stdout=StringIO())
        logs = "\n".join(captured.output)
        self.assertIn("Ingestion failed", logs)
        self.assertNotIn("Ingestion completed", logs)
        self.assertEqual(Patent.objects.count(), 0)
