# 003 — Linked interface updates

Observed 2026-11-16, 22:50 UTC. [Raw JSON](results/003-linked-interface.json).

## Setup and method

- Supplied sample: 640 patents, 64 weekly JSON batches; index already populated.
- Apple M1 (8 cores), 8 GB RAM; macOS 27.0.1 arm64. API/PostgreSQL in local Docker;
  production Vite bundle on loopback port 4173, proxied to API port 8000.
- agent-browser 0.39.1, headless Chrome 155; no CPU/network throttling.
- Start in browse (640), select `B60B` (298), render 20 results and all filtered
  classification/week counts. Clear classification between trials.
- 3 discarded warmups, then 20 measured selections. Warm browser/database;
  not cold-cache or controlled external-network measurements.
- `performance.measure("explore-update")` starts in the applied-filter handler
  and ends at the second animation frame after React commits the accepted
  response. Includes API, parsing, React and a paint opportunity, not physical
  display presentation. Frame cadence contributes substantially at this size.
- Median = average of sorted samples 10/11; p95 = nearest rank, sample 19 of 20.

| Metric | Milliseconds |
|---|---:|
| Median | 50.0 |
| p95 | 51.3 |
| Min | 48.8 |
| Max | 65.9 |

No speedup or 10-million-patent performance claim follows from these results.
This recorded baseline predates the Figma visual refinement and numbered
pagination. Later development-mode browser runs are regression checks, not
replacement production timing baselines.

## Reproduce

Follow root README Part 1 setup with the supplied sample, then:

```sh
make frontend-install
make frontend-build
make frontend-preview
# Second terminal, API and preview running:
make frontend-test
```

Python 3 and `agent-browser` with browser binaries are required;
[setup](../../frontend/README.md). New output goes to ignored
`artifacts/frontend-exploration.json`, never this baseline.

## Correctness verification

The same runner checks full-set counts, parent/child sums, pagination, original
evidence, parent→child drill-down, weekly selection, retained filters on new
queries, independent removal, result-card filtering, empty results, 422 errors,
network error/retry and reversed dates. Controlled promises complete requests in
reverse order, deliberately ignoring abort; old successes/errors cannot replace
the latest response. Old views are absent during loading/errors.

Separately, 71 backend tests still pass. A 390px viewport had no horizontal
overflow. axe WCAG 2 A/AA reported no violations after contrast/pagination fixes,
but retained contrast checks requiring human review; no full accessibility
certification is claimed.

## At 10 million patents

Replace Python scans with persisted/indexed source dates and SQL aggregation over
the same filtered candidates. Bound evidence/facet payloads, consider cursor
pagination, measure plans and production p95 under concurrency. Keep one coherent
response (or snapshot/version token if split) and the latest-request guard.
Virtualize larger pages instead of rendering unbounded cards. These are proposed
scale changes, not implemented optimizations.
