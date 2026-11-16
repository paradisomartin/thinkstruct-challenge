# 002 — Correct weighted-ranking service baseline

## Purpose and correction

Supersedes [001](001-search-baseline.md), whose ORM rank expression re-tokenized
the stored vector's textual representation. Ranking now uses
`SearchRank(F("search_vector"), ...)`, and passage ranking uses `F("vector")`.
Stored vectors/GIN and candidate-match semantics were already correct.
Result order, excerpts and timing can change; this is a correctness fix, not an
apples-to-apples performance optimization of the same output.

Regression tests compare service scores against direct PostgreSQL `ts_rank`.
IDs deliberately oppose weight order; tests also cover passage term frequency,
real ties, pagination, absent scalar fields, punctuation, apostrophes, hyphens,
repeated terms and explicit English configuration.

## Reproduction and environment

```sh
make dev
make ingest
make reindex
make test
make benchmark
make api-test
```

Run from repository root with the supplied data and environment configured.
New measurements go to ignored `artifacts/search-benchmark.json`; the selected
[raw snapshot](results/002-search-ranking-fix.json) preserves this run.

- Observed **2026-11-16, 19:40 UTC**. Same sample: 640 patents / 31,671 passages,
  all 640 patent vectors indexed. Dataset manifest SHA-256:
  `94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6`.
- Host Apple M1, 8 logical CPUs, 8 GiB RAM. Docker Desktop VM exposes 8 CPUs and
  4,106,539,008 bytes RAM. Python 3.13.18, PostgreSQL 18.7, aarch64.
- Same protocol as 001: 3 warmups and 20 measured calls per variant, alternating
  order, sequential execution, limit 20 / offset 0, warm caches without resets.
- `perf_counter` measures the complete service call: validation, SQL count/rank,
  pagination, literal metadata filtering and excerpt selection. Startup, ingestion,
  indexing, HTTP, JSON serialization and response verification are excluded.
- p50 median; p95 nearest-rank `ceil(0.95*n)`. Samples and summaries rounded
  independently to 0.001 ms. Response hashes must remain stable within each
  variant, filtered counts cannot exceed baseline, and concurrent writes are
  excluded by methodology rather than locking.

## Observed results

| Query | Added filter | Matches without → with | p50 ms without → with | p95 ms without → with |
|---|---|---:|---:|---:|
| `wheel spoke` | Classification `B60B` | 114 → 98 | 124.975 → 146.207 | 131.204 → 154.844 |
| `pneumatic tire` | Classification `B60C` | 169 → 158 | 136.037 → 132.775 | 210.656 → 179.917 |
| `wheel` | Literal title token `wheel` | 417 → 163 | 140.051 → 144.832 | 165.303 → 172.886 |
| `pressure` | Literal abstract token `pressure` | 215 → 29 | 110.399 → 103.944 | 133.190 → 171.914 |

## Interpretation and limits

Filters do **not** uniformly improve latency: two p50 values rose, two fell, and
the abstract filter's lower p50 coexists with a higher p95. Twenty observations
on a small warm sample do not establish statistical significance or capacity.
Candidates, selected patents and excerpt workloads differ between variants.

PostgreSQL can use GIN for candidate lookup; ranking and page-local excerpt
tokenization still cost work. Literal title/abstract constraints scan candidate
metadata in Python, an intentional sample-scale compromise. At scale, evaluate
indexed normalized metadata, classification-prefix indexes, bounded evidence
selection and pagination strategies using representative workloads and plans.
None of those optimizations is claimed measured here.

This is neither an HTTP/load/cold-cache test nor a relevance evaluation.
55 automated tests and 8 live Bruno requests / 9 script tests passed separately;
they are correctness checks, not timing samples. Part 3 remains unselected.
