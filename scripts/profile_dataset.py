"""Read-only dataset discovery; no search engine or third-party dependencies."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


FIELDS = (
    "title", "doc_number", "abstract", "detailed_description",
    "claims", "bibtex", "classification", "filename",
)


def empty(value):
    return value is None or (
        isinstance(value, (str, list, dict)) and not value
    ) or (isinstance(value, str) and not value.strip())


def distribution(values):
    if not values:
        return None
    values = sorted(values)
    n = len(values)
    median = (values[(n - 1) // 2] + values[n // 2]) / 2
    return {"min": values[0], "median": median, "max": values[-1],
            "total": sum(values)}


def profile(directory):
    files = sorted(directory.rglob("*.json"))
    report = {"directory": str(directory), "file_count": len(files),
              "bytes": sum(p.stat().st_size for p in files)}
    manifest = hashlib.sha256()
    file_records = {}
    errors = []
    shapes = Counter()
    rows = []
    locations = defaultdict(list)
    for path in files:
        raw = path.read_bytes()
        name = path.relative_to(directory).as_posix()
        digest = hashlib.sha256(raw).hexdigest()
        manifest.update(f"{name}\t{digest}\n".encode())
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            errors.append({"file": name, "error": str(exc)})
            continue
        shapes[type(data).__name__] += 1
        if not isinstance(data, list):
            errors.append({"file": name, "error": "Expected a top-level list"})
            continue
        file_records[name] = len(data)
        for i, row in enumerate(data):
            if not isinstance(row, dict):
                errors.append({"file": name, "index": i,
                               "error": "Expected an object"})
                continue
            rows.append(row)
            if isinstance(row.get("doc_number"), str):
                locations[row["doc_number"]].append(f"{name}:{i}")
    report.update(manifest_sha256=manifest.hexdigest(), errors=errors,
                  top_level_types=dict(shapes), file_records=file_records,
                  record_count=len(rows))
    report["key_counts"] = dict(Counter(k for row in rows for k in row))
    report["fields"] = {}
    for field in FIELDS:
        values = [row[field] for row in rows if field in row]
        report["fields"][field] = {
            "missing_key": len(rows) - len(values),
            "null": sum(v is None for v in values),
            "empty_non_null": sum(v is not None and empty(v) for v in values),
            "types": dict(Counter(type(v).__name__ for v in values)),
            "lengths": distribution([len(v) for v in values
                                     if isinstance(v, (str, list, dict))]),
        }
    report["duplicate_ids"] = {k: v for k, v in locations.items() if len(v) > 1}
    report["unique_string_ids"] = len(locations)
    titles = Counter(row["title"] for row in rows if isinstance(row.get("title"), str))
    report["repeated_titles"] = {
        "groups": sum(n > 1 for n in titles.values()),
        "records": sum(n for n in titles.values() if n > 1),
    }
    report["id_patterns"] = dict(Counter(
        "11 digits" if isinstance(row.get("doc_number"), str)
        and re.fullmatch(r"\d{11}", row["doc_number"]) else "other"
        for row in rows
    ))
    report["passages"] = {}
    for field in ("claims", "detailed_description"):
        values = [row[field] for row in rows if isinstance(row.get(field), list)]
        items = [item for value in values for item in value]
        report["passages"][field] = {
            "item_types": dict(Counter(type(v).__name__ for v in items)),
            "empty_items": sum(empty(v) for v in items),
            "records_with_empty_items": sum(any(empty(v) for v in x) for x in values),
            "records_with_no_usable_text": sum(
                not any(isinstance(v, str) and v.strip() for v in x) for x in values
            ),
            "items_containing_cancel": sum(
                isinstance(v, str) and "cancel" in v.lower() for v in items
            ),
            "nonempty_item_characters": distribution(
                [len(v) for v in items if isinstance(v, str) and v.strip()]
            ),
            "examples": [
                {"doc_number": row.get("doc_number"),
                 "items": [{"source_index": i, "text": v[:400]}
                           for i, v in enumerate(row.get(field, []))
                           if isinstance(v, str) and v.strip()][:2]}
                for row in rows[:2]
            ],
        }
    codes = Counter(row["classification"] for row in rows
                    if isinstance(row.get("classification"), str))
    report["classifications"] = {
        "unique": len(codes), "codes": dict(sorted(codes.items())),
        "prefix4": dict(Counter(
            code[:4] for row in rows
            if isinstance((code := row.get("classification")), str)
        )),
        "outside_observed_pattern": [
            code for code in codes if not re.fullmatch(r"B60[A-Z]\d+FI", code)
        ],
    }
    file_dates = []
    for name in file_records:
        match = re.fullmatch(r"patents_ipa(\d{6})\.json", name)
        if match:
            file_dates.append(datetime.strptime(match[1], "%y%m%d").date().isoformat())
    xml_dates = []
    mismatches = []
    kinds = Counter()
    unmatched = []
    for row in rows:
        match = re.fullmatch(r"US(\d+)(A\d)-(\d{8})\.XML", row.get("filename", ""))
        if match:
            kinds[match[2]] += 1
            xml_dates.append(datetime.strptime(match[3], "%Y%m%d").date().isoformat())
            if match[1] != row.get("doc_number"):
                mismatches.append(row.get("doc_number"))
        else:
            unmatched.append(row.get("filename"))
    report["dates"] = {
        "json_filename_date_count": len(file_dates),
        "json_filename_date_range": [min(file_dates), max(file_dates)] if file_dates else [],
        "xml_filename_date_count": len(xml_dates),
        "xml_filename_date_range": [min(xml_dates), max(xml_dates)] if xml_dates else [],
        "xml_document_number_mismatches": mismatches,
        "xml_kind_codes": dict(kinds),
        "unmatched_xml_filenames": unmatched,
        "explicit_date_keys": sorted({k for row in rows for k in row
                                     if "date" in k.lower()}),
    }
    report["representative_record"] = {
        k: (v[:300] if isinstance(v, str) else {"type": type(v).__name__, "length": len(v)})
        for k, v in rows[0].items()
    } if rows else None
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error("Dataset directory does not exist")
    result = profile(args.directory)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["file_count"] or result["errors"]:
        raise SystemExit(1)
