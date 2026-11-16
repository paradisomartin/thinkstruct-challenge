# 001 — Warm filtered/unfiltered service baseline

**Historical / superseded:** This run used an incorrect ORM ranking expression:
`SearchRank("search_vector", ...)` re-tokenized vector text, losing the intended
weights/positions. The stored index and match counts were unaffected, but ranking,
excerpt ordering and timings do not describe the intended algorithm.
Retained unchanged raw measurements for traceability; use
[report 002](002-search-ranking-fix.md) for the corrected implementation.

## Question and historical command

How does adding a classification or literal metadata constraint affect the
complete search service's latency on the supplied sample?

From the repository root, after configuring the environment and supplying data:

```sh
make dev
make ingest
make reindex
make benchmark
# Optional: make benchmark ARGS='--repetitions 30 --warmups 5 --limit 20'
```

Running these commands now measures the corrected implementation, not this
historical defect. The last command writes `artifacts/search-benchmark.json`,
not the versioned
[baseline snapshot](results/001-search-baseline.json). The snapshot retains all
report values, including individual samples, requests and response hashes.
No patent text or credentials are included.

## Environment and method

- Observed on **2026-11-16, 19:26 UTC**; 640 patents / 31,671 passages,
  all patent vectors rebuilt. Supplied dataset manifest SHA-256:
  `94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6`.
- Host: Apple M1, 8 logical CPUs, 8 GiB RAM. Docker Desktop VM exposes 8 CPUs
  and 4,106,539,008 bytes RAM. Python 3.13.18 / PostgreSQL 18.7 / aarch64.
- Each variant receives **3 warmups + 20 measured calls**, sequentially with
  alternating filtered/unfiltered order, limit 20 / offset 0.
- Caches are warm, not reset. Wall-clock `perf_counter` surrounds
  `search_patents`: validation, SQL count/rank/paging, Python literal filtering
  where requested, and original-text excerpt selection.
- Excludes startup, ingestion/indexing, HTTP and JSON serialization. Full response
  hashing/verification happens outside the timing boundary.
- p50 is the median; p95 is nearest-rank `ceil(0.95*n)`. Samples and summaries
  are rounded independently to 0.001 ms.
- Each variant's full response hash must stay stable across warmup/measured calls;
  filtered counts cannot exceed their baseline. The command requires a nonempty,
  fully indexed database. It assumes no concurrent writes.

## Observed results

| Query | Added filter | Matches without → with | p50 ms without → with | p95 ms without → with |
|---|---|---:|---:|---:|
| `wheel spoke` | Classification `B60B` | 114 → 98 | 304.747 → 269.126 | 314.504 → 274.016 |
| `pneumatic tire` | Classification `B60C` | 169 → 158 | 470.902 → 441.178 | 479.314 → 448.198 |
| `wheel` | Literal title token `wheel` | 417 → 163 | 958.553 → 466.568 | 967.107 → 473.172 |
| `pressure` | Literal abstract token `pressure` | 215 → 29 | 613.005 → 155.682 | 631.971 → 161.181 |

## Interpretation and limits

Filters lowered observed p50 in this run, but it is not a load test, a cold-cache
test or a claim about 10 million patents. Different filters select different pages
and excerpt workloads; changes cannot be attributed solely to index lookup.
The JSON snapshot is authoritative for this execution.

No relevance evaluation was performed. This baseline does not satisfy Part 3.

## Query-plan spot check and efficiency

An additional `EXPLAIN (ANALYZE, BUFFERS)` on candidate-ID lookup for `wheel spoke`
was recorded as using a bitmap scan on `patent_search_vector_gin` with and
without `B60B`.
The classification filter removed 16 of 114 candidates. Reproduce that limited
plan inspection in PostgreSQL with (the plan output was not preserved):

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT doc_number FROM patents_patent
WHERE search_vector @@ plainto_tsquery('english', 'wheel spoke');

EXPLAIN (ANALYZE, BUFFERS)
SELECT doc_number FROM patents_patent
WHERE search_vector @@ plainto_tsquery('english', 'wheel spoke')
  AND classification LIKE 'B60B%';
```

These single-plan timings are not the service benchmark: they exclude count,
ranking, paging and evidence. GIN indexes precomputed patent terms; native
`ts_rank` still ranks candidates, and page-local excerpt selection tokenizes
passages again.

At scale, persist indexed literal tokens/normalized titles instead of scanning
candidate metadata in Python; evaluate prefix indexes against real plans, bound
evidence work, and reconsider passage indexes and pagination using measured
workloads. None of those changes was benchmarked here. The explicit all-patent
rebuild is a small-sample design, not a streaming indexer.
