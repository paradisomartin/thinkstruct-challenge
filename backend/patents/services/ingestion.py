"""Small-sample, fail-closed ingestion. Raw records and source positions are retained."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from django.db import transaction

from patents.models import Passage, Patent


CANCELED_MARKER = re.compile(
    r"^\s*(?:\d+\s*(?:[-–]\s*\d+)?\s*\.?\s*)?"
    r"\(\s*cancel(?:ed|led)\s*\)\s*\.?\s*$",
    re.IGNORECASE,
)
SCALAR_FIELDS = ("title", "abstract", "classification", "bibtex", "filename")


class IngestionError(ValueError):
    pass


def normalize_record(raw, source_file, record_index):
    if not isinstance(raw, dict):
        raise IngestionError("Record must be an object")
    doc_number = raw.get("doc_number")
    if (
        not isinstance(doc_number, str)
        or not doc_number.strip()
        or doc_number != doc_number.strip()
        or len(doc_number) > 64
    ):
        raise IngestionError("doc_number must be a nonblank string of at most 64 characters without edge whitespace")
    metadata = {}
    for field in SCALAR_FIELDS:
        value = raw.get(field)
        if value is not None and not isinstance(value, str):
            raise IngestionError(f"{field} must be a string or null")
        metadata[field] = value if value and value.strip() else None
    passages = []
    skipped = Counter()
    for field in Passage.SourceField.values:
        values = raw.get(field)
        if values is None:
            values = []
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise IngestionError(f"{field} must be a list of strings or null")
        for index, text in enumerate(values):
            if not text.strip():
                skipped["blank_entries"] += 1
            elif field == "claims" and CANCELED_MARKER.fullmatch(text):
                skipped["canceled_markers"] += 1
            else:
                passages.append({"source_field": field, "source_index": index, "text": text})
    if not passages and not any(metadata[field] for field in ("title", "abstract")):
        raise IngestionError("Record has no meaningful searchable text")
    # Canonical JSON distinguishes content changes, not dictionary key order.
    digest = hashlib.sha256(
        json.dumps(raw, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
    ).hexdigest()
    return {
        "doc_number": doc_number,
        **metadata,
        "source_file": source_file,
        "record_index": record_index,
        "content_sha256": digest,
        "raw_record": raw,
    }, passages, skipped


def ingest_directory(directory, dry_run=False):
    directory = Path(directory)
    if not directory.is_dir():
        raise IngestionError(f"Dataset directory does not exist: {directory}")
    paths = sorted(directory.rglob("*.json"))
    if not paths:
        raise IngestionError("Dataset directory contains no JSON files")
    prepared = []
    seen = set()
    counts = Counter(files=len(paths), records=0, created=0, unchanged=0, passages_created=0,
                     blank_entries=0, canceled_markers=0)
    # Validate the entire small sample before making any database changes.
    for path in paths:
        source_file = path.relative_to(directory).as_posix()
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise IngestionError(f"{source_file}: invalid/unreadable JSON: {exc}") from exc
        if not isinstance(rows, list):
            raise IngestionError(f"{source_file}: expected a top-level list")
        for index, raw in enumerate(rows):
            try:
                metadata, passages, skipped = normalize_record(raw, source_file, index)
            except ValueError as exc:
                raise IngestionError(f"{source_file}[{index}]: {exc}") from exc
            doc_number = metadata["doc_number"]
            if doc_number in seen:
                raise IngestionError(f"{source_file}[{index}]: duplicate doc_number {doc_number}")
            seen.add(doc_number)
            counts["records"] += 1
            counts.update(skipped)
            prepared.append((metadata, passages))
    with transaction.atomic():
        existing = {
            patent.doc_number: patent
            for patent in Patent.objects.filter(pk__in=seen).only(
                "doc_number", "content_sha256", "source_file", "record_index"
            )
        }
        for metadata, passages in prepared:
            patent = existing.get(metadata["doc_number"])
            if patent:
                if any(
                    getattr(patent, field) != metadata[field]
                    for field in ("content_sha256", "source_file", "record_index")
                ):
                    raise IngestionError(f"Conflicting existing doc_number {patent.doc_number}; no overwrite allowed")
                counts["unchanged"] += 1
                continue
            counts["created"] += 1
            counts["passages_created"] += len(passages)
            if not dry_run:
                patent = Patent.objects.create(**metadata)
                Passage.objects.bulk_create(
                    [Passage(patent=patent, **passage) for passage in passages],
                    batch_size=1000,
                )
    return {**dict(counts), "dry_run": dry_run}
