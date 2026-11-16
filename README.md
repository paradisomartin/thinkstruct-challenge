# Thinkstruct — Patent Search

A small workspace for exploring vehicle patents: search their text, narrow by
classification or keywords, and inspect the original passages behind a match.
The results list, classification breakdown and weekly timeline stay in sync as
you change filters.

<img width="1866" height="810" alt="Thinkstruct patent search workspace with linked results, classifications and source weeks" src="https://github.com/user-attachments/assets/5347a860-7979-43ab-9509-65069e0f66c6" />

Built with **Django, Django Ninja, PostgreSQL and React**, with Tailwind CSS and
daisyUI. The [Figma design](https://www.figma.com/design/nhVo8ZpPfyB6G3dEk62ijB/Thinkstruct-Challenge---Martin-Paradiso?node-id=3-5)
guided the desktop layout.

## What's included

| Challenge part | Delivered |
|---|---|
| **1 — Search** | Text search, structured filters, ranked results, traceable evidence and a filtered/unfiltered benchmark |
| **2 — Scale** | AWS architecture, approximate costs and a locally verified container ingestion PoC |
| **3 — Interface at Scale** | Three linked views, removable filters, stale-response protection, tests and measured update times |

The code is implemented and tested on the supplied sample.
**The remaining submission item is the ~2-minute Part 2/3 recording; no video link is available yet.**
The [original brief](docs/reference/thinkstruct-coding-task.pdf) is included for reference.

## Run locally

### Recommended: everything in Docker

You need Make, Docker and Docker Compose v2 with `--wait` support. Place the
separately supplied JSON files in `data/raw/`; they are not included in Git.
See [data placement](data/README.md).

From the repository root, create `.env` **only if you don't already have one**:

```sh
cp .env.example .env
```

Replace `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD`, then run:

```sh
make dev-all
make ingest ARGS=--dry-run
make ingest
make reindex
```

Open **http://127.0.0.1:5173**.
The API docs are at **http://localhost:8000/api/docs**.

`make dev-all` builds the images, applies migrations and starts the three
services. Ingestion and indexing are explicit steps; they are not repeated on
every startup. The first frontend startup downloads Node and installs the
locked dependencies.

- Already using port 5173? Use `make dev-all FRONTEND_PORT=5174`.
- To stop everything: `make stop`. To inspect services: `make status`.
- Database data persists across restarts. **Do not run `docker compose down -v`**
  unless you intend to delete it.

These are local development servers, bound to loopback, not a production deployment.
Docker must be on PATH, or set `DOCKER=/path/to/docker`; Make also recognizes
Docker Desktop's bundled executable on macOS.

### Alternative: run React on the host

With Node.js 22.12+ and npm installed:

```sh
make dev
# Run ingestion and indexing above if not already done.
make frontend-install
make frontend-dev
```

`make dev` starts only Django and PostgreSQL. Stop the Docker frontend first
with `make frontend-docker-stop` if it occupies the same port.
Host Vite is stopped with Ctrl+C, not `make stop`.
[Frontend setup, proxy and test details](frontend/README.md).

## Try the linked views

1. Start with **Clear all**: the supplied sample has **640 patents**.
2. Search `wheel spoke`: **114 matches**.
3. Select `B60`, then `B60B`: **98 matches**.
4. In **Advanced filters**, add `wheel` to **Title keywords**: **55 matches**.
5. Select a source week. All three views update together.
6. Remove filters in any order, or enter a new query: the other filters stay applied.

Counts cover **all filtered matches**, not just the current page.
“Source week” means the date in the weekly JSON filename, not a verified legal
filing date. Date ranges are inclusive.

### Use the API directly

```sh
curl --get http://localhost:8000/api/v1/patents/search \
  --data-urlencode 'query=wheel spoke' \
  --data-urlencode 'classification_prefix=B60B' \
  --data-urlencode 'title_keywords=wheel' \
  --data-urlencode 'limit=5'
```

For exact-title lookup, use `title_exact=spoke`. For browse and linked-view
counts, use `/api/v1/patents/explore`; omit query/filters to browse everything.

All constraints combine with AND. Text search uses English stemming;
title/abstract keywords are literal tokens. Repeat API keyword parameters for
multiple terms. Exact titles ignore case and collapsed whitespace.
Stop-word-only queries return 422. Pagination defaults to 20 results, with a
maximum of 100 per page. [Full search contract](docs/decisions/001-search-contract.md)
and [exploration contract](docs/decisions/005-enhancement.md).

## How it works

### Part 1: search and evidence

PostgreSQL handles both text search and structured filters. Each patent has a
persisted English `tsvector` and a GIN index; native `ts_rank` ranks matches.
Title text has weight A, abstract/claims B, and descriptions D. This keeps the
implementation small and explainable without adding embedding infrastructure.

Results include original-text excerpts and source positions. An excerpt may
explain only part of a query that matches across fields; it is not a generated
summary or a legal relevance assessment.

The sample contains **64 files, 640 patents and 31,671 usable passages**.
All **119 patents without usable descriptions** are retained. Blank or canceled
passages are excluded from search, while original records and positions remain
available for traceability. Reimporting identical files leaves the data unchanged;
conflicting content or provenance aborts the import instead of overwriting it.
[Data policy](docs/decisions/002-data-policy.md).

Run `make reindex` after importing or changing text. Index freshness is not
automatic. [Local architecture](docs/architecture/part-1-local.md) and
[backend guide](backend/README.md).

### Part 2: a path to larger scale

The [AWS proposal](docs/architecture/part-2-aws.md) separates Fargate API tasks
from on-demand ingestion, using RDS PostgreSQL and immutable sources in S3.
It covers retries, import status, networking and backups.

The [cost model](docs/architecture/part-2-costs.md) estimates about **$1,120/month**
for Single-AZ or **$1,966/month** with an RDS standby, before 20% contingency.
These are assumptions, not measured spending or validated capacity.

The [local PoC](docs/architecture/part-2-poc.md) demonstrates containerized
ingestion, indexing, idempotent reimport and API checks on the sample.
Its isolated reproduction requires Compose 2.24.4+.
**No AWS resources were deployed, and 10-million-patent capacity is not claimed.**

### Part 3: keeping the views consistent

**Interface at Scale** was chosen because narrowing a result set is more useful
when you can see its distribution and evidence alongside the list.

`/api/v1/patents/explore` computes results and counts in one read-only PostgreSQL
`REPEATABLE READ` snapshot. React applies that response as a whole.
When filters change, old views are cleared until the new response arrives.
Requests are canceled, and a separate request ID prevents older successes
or errors from replacing the latest state even if cancellation is ignored.

At 10 million patents, Python metadata scans would need to become indexed
database filtering and aggregation. Evidence work, facet payloads and pagination
would need bounds, with query-plan and concurrency measurements. The coherent
response and latest-request guard would still matter. These scale changes are
proposals, not implemented optimizations.

## Tests

```sh
make check                    # Django checks and migration consistency
make test                     # 71 backend tests; no supplied dataset needed
make frontend-docker-test     # 4 Vitest tests; Docker frontend must be running
make api-test                 # Bruno: 9 requests / 10 tests
make frontend-test URL=http://127.0.0.1:5173
```

The last command runs browser checks against the live app and requires the
640-patent sample, Python 3 and `agent-browser`.
It covers linked counts, filters, pagination, empty/error/retry states and
out-of-order responses. Vitest uses synthetic HTTP responses; it does not replace
these live checks. See [browser setup](frontend/README.md#verification-and-measurements)
and [Bruno setup](tools/bruno/README.md).

Without a running frontend container, use `make frontend-unit-test` for Vitest
on the host.

## Measurements

### Search with and without filters

On 640 patents / 31,671 passages, with 3 warmups and 20 measured calls per
variant, alternating order, limit 20 and warm caches:

| Query | Added filter | Matches without → with | Median ms without → with |
|---|---|---:|---:|
| `wheel spoke` | Classification `B60B` | 114 → 98 | 124.975 → 146.207 |
| `pneumatic tire` | Classification `B60C` | 169 → 158 | 136.037 → 132.775 |
| `wheel` | Title token `wheel` | 417 → 163 | 140.051 → 144.832 |
| `pressure` | Abstract token `pressure` | 215 → 29 | 110.399 → 103.944 |

Filters had mixed effects: fewer candidates do not guarantee faster excerpt
selection. These are sequential service timings, excluding HTTP, on an Apple M1
(8 CPUs, 8 GiB; Docker VM about 3.82 GiB).
They predate the exploration refactor.
[Method and raw results](docs/benchmarks/002-search-ranking-fix.md).
Reproduce with `make benchmark`.

### Filter-to-render time

Selecting `B60B` from browse (640 → 298 matches, 20 rendered results) took
**50.0 ms median / 51.3 ms p95** over 20 warm updates after 3 warmups.
This used a local production bundle, headless Chrome 155 and an Apple M1 / 8 GB Mac.
Timing runs from the filter handler through the second animation frame after
the views commit, including API time and a paint opportunity.
It is not a remote-network or at-scale benchmark, and predates the Figma styling.
[Method and raw results](docs/benchmarks/003-linked-interface.md).

To reproduce, keep the API running:

```sh
make frontend-build
make frontend-preview
# In another terminal:
make frontend-test
```

This production-bundle measurement requires host Node/npm.
New benchmark runs write to ignored `artifacts/`, never over the recorded baselines.

## Limits and remaining work

- English lexical matching can miss paraphrases; ranking weights are heuristics.
  No relevance evaluation or legal novelty assessment was performed.
- Ingestion, metadata scans and full index rebuilds are sample-scale.
  PostgreSQL full-text size/position limits matter for long documents.
- The app has no authentication and is intended for local review.
- **Still to add:** an accessible ~2-minute recording explaining Parts 2 and 3.

More detail: [architecture](docs/architecture/README.md) ·
[decisions](docs/decisions/README.md) · [benchmarks](docs/benchmarks/README.md) ·
[engineering journal](docs/journal/README.md).
