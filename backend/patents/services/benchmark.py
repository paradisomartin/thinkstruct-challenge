"""Warm, sequential service timing; not HTTP/load testing or relevance evaluation."""

import hashlib
import json
import math
import platform
import statistics
from datetime import datetime, timezone
from time import perf_counter

from django.db import connection

from patents.models import Passage, Patent
from patents.services.search import search_patents


SCENARIOS = (
    ("wheel_classification", "wheel spoke", {"classification_prefix": "B60B"}),
    ("tire_classification", "pneumatic tire", {"classification_prefix": "B60C"}),
    ("wheel_title", "wheel", {"title_keywords": ["wheel"]}),
    ("pressure_abstract", "pressure", {"abstract_keywords": ["pressure"]}),
)


def summarize(samples):
    ordered = sorted(samples)
    return {
        "p50_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(ordered[math.ceil(0.95 * len(ordered)) - 1], 3),
        "samples_ms": [round(value, 3) for value in samples],
    }


def benchmark_search(*, repetitions=20, warmups=3, limit=20):
    if type(repetitions) is not int or repetitions < 1:
        raise ValueError("repetitions must be a positive integer")
    if type(warmups) is not int or warmups < 1:
        raise ValueError("warmups must be a positive integer")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    count = Patent.objects.count()
    if not count or Patent.objects.filter(search_vector__isnull=True).exists():
        raise ValueError("Ingest patents and rebuild all search vectors before benchmarking")
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('server_version')")
        postgres_version = cursor.fetchone()[0]
    results = []
    for name, query, filters in SCENARIOS:
        variants = {
            "unfiltered": {"query": query, "limit": limit},
            "filtered": {"query": query, "limit": limit, **filters},
        }
        samples = {key: [] for key in variants}
        fingerprints = {}
        totals = {}

        def run(key, timed):
            start = perf_counter()
            response = search_patents(**variants[key])
            elapsed = (perf_counter() - start) * 1000
            # Verification/serialization are outside the measured service call.
            fingerprint = hashlib.sha256(
                json.dumps(response, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest()
            if key in fingerprints and fingerprint != fingerprints[key]:
                raise ValueError("Results changed during benchmark; rerun on a stable database")
            fingerprints[key] = fingerprint
            totals[key] = response["total_matches"]
            if timed:
                samples[key].append(elapsed)

        for iteration in range(warmups + repetitions):
            order = ("unfiltered", "filtered") if iteration % 2 == 0 else ("filtered", "unfiltered")
            for key in order:
                run(key, timed=iteration >= warmups)
        if totals["filtered"] > totals["unfiltered"]:
            raise ValueError("Filtered count exceeds baseline count")
        results.append({
            "name": name,
            "variants": {
                key: {
                    "request": variants[key], "total_matches": totals[key],
                    "response_sha256": fingerprints[key], **summarize(samples[key]),
                } for key in variants
            },
        })
    return {
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {"patents": count, "passages": Passage.objects.count(), "indexed": count},
        "runtime": {
            "python": platform.python_version(), "machine": platform.machine(),
            "postgresql": postgres_version,
        },
        "method": {
            "boundary": "search_patents including validation, count, rank, paging, excerpts",
            "excludes": "startup, ingestion/rebuild, HTTP, JSON serialization, fingerprint verification",
            "cache": "warm; no OS/PostgreSQL cache reset",
            "order": "sequential; alternating variant order each iteration",
            "repetitions": repetitions, "warmups_per_variant": warmups,
            "limit": limit, "offset": 0,
            "aggregation": "p50 median; p95 nearest-rank ceil(0.95*n)",
        },
        "scenarios": results,
    }
