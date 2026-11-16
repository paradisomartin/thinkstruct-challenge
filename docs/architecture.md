# Architecture — current slice and Part 2 boundary

**Status:** Local ingestion/search and warm service measurements are verified.
The Part 2 at-scale design, cost breakdown,
and designated PoC are not complete. This is not a production-capacity claim.

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

The local development HTTP server exposes patent search, health and generated
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
Tests are summarized in the [README](../README.md); warm measurements are in the
[baseline report](benchmarks/001-search-baseline.md).
The [accepted contract](decisions/001-search-contract.md)
is independent of HTTP.

## At-scale candidate — still to evaluate

For the brief's ~10 million patents: S3 sources, ECS Fargate API/ingestion tasks,
RDS PostgreSQL, and optional static frontend hosting/CDN. Fargate removes host
management, not database/index bottlenecks. Queues, retries, and status tracking
need workload justification. Current all-in-memory/all-or-nothing ingestion
would need bounded batches and durable progress; conflicting patent versions
also need an explicit policy.

Before completing Part 2, specify query volume, freshness, passage/index sizing,
retention, region/provider pricing, failure/retry behavior, and observability.
Estimate storage, database, compute, networking, and monitoring costs from those
explicit assumptions. **No cost estimates or production capacity measured yet.**
Select and explain one narrow PoC; do not automatically relabel current work.

Keep simple diagrams inline. Add editable/exported assets under `docs/assets/`
only when they clarify an actual design. AWS deployment remains an optional extra.
