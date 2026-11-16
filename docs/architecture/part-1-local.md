# Part 1 — Implemented local architecture

**Status:** Local ingestion/search and warm service measurements are verified.
This document describes the implemented sample-scale system, not a production
deployment. The [Part 2 AWS proposal](part-2-aws.md) explains what would change
for a larger corpus.

## Implemented local pipeline

```text
JSON files (read-only mount)
    → management command → ingestion service
    → validate/normalize entire sample
    → PostgreSQL transaction → Patent + Passage rows
```

Django models/migrations define persistence. Services coordinate use cases;
commands adapt CLI inputs/errors. Raw JSON, source filename, record position,
and original passage positions preserve provenance. Invalid input/conflicting IDs
abort the import; unchanged content/provenance is skipped. An explicit rebuild
derives patent-level English search vectors with a GIN index. No queue/scheduler.

The local development HTTP server exposes `/api/v1/patents/search`, health and generated
OpenAPI/docs. Health uses `SELECT 1` to test database connectivity, not dataset or
index readiness. Compose binds the API to host loopback and uses this endpoint
for readiness. Make wraps local tasks; English stage logs go to stderr separately
from command JSON stdout. Bruno has versioned HTTP requests and script tests.

## Implemented search path

```text
query + structured filters → Ninja schemas/routes → search service
    → PostgreSQL eligible candidates + lexical ranking
    → patent results with traceable excerpts
```

A PostgreSQL GIN inverted index accelerates term lookup; native `ts_rank` ranks
eligible patents, with document-number ties. Literal title/abstract constraints
scan candidate metadata in Python before SQL count/rank/pagination: sample-scale,
not an indexed large-scale strategy. Evidence re-tokenizes page-local passages.
Tests are summarized in the [project README](../../README.md); warm measurements are in the
[corrected baseline report](../benchmarks/002-search-ranking-fix.md).
The [accepted contract](../decisions/001-search-contract.md)
is independent of HTTP.

The Part 3 `/api/v1/patents/explore` endpoint reuses this search path and adds
source-date filtering and full-result-set classification/date counts in one
read-only, repeatable-read transaction. Aggregation scans compact metadata in
Python; [contract and limits](../decisions/005-enhancement.md).

## Boundary with Part 2

Whole-sample ingestion, full explicit index rebuilding and Python metadata scans
are deliberate local compromises. They are not evidence of capacity at ten
million patents. Proposed batching, indexed filters, operational status and AWS
components belong in the [Part 2 design](part-2-aws.md), not this implemented path.
