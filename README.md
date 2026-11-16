# Thinkstruct — Patent Search

**Goal:** Help a reviewer find vehicle-related patent applications using text
and classification/title/abstract filters, with ranked patents and traceable excerpts.
See the [original brief](docs/reference/thinkstruct-coding-task.pdf) and
[accepted contract](docs/decisions/001-search-contract.md).

**Delivery status:** Part 1 search and local benchmarks are implemented. Part 2
has an AWS design, cost model and locally verified container PoC. Part 3
**Interface at Scale** has three linked React views, stale-response protection,
frontend integration/E2E checks and recorded sample-scale update measurements.
The remaining submission requirement is an accessible ~2-minute Part 2/3 recording;
no recording link has been published yet.

## Structure and approach

Django provides persistence and migrations; Django Ninja exposes typed HTTP routes
and OpenAPI. PostgreSQL provides English lexical retrieval and structured filters,
without embedding infrastructure. One weighted search vector per patent and native
`ts_rank` keep counts and ranking at patent level; original passage positions make excerpts
traceable. [Local architecture](docs/architecture/part-1-local.md).
`backend/` owns Django, `frontend/` owns React, and root Compose orchestrates the
API/database plus an optional development frontend. Optional rationale and evidence
are indexed under `docs/`.

## Run Part 1

Prerequisites: Make, Docker Engine running, Docker Compose v2 with `--wait` support,
and the separately supplied JSON files extracted into `data/raw/`.
The isolated Part 2 PoC requires Compose 2.24.4+. Data is not published in Git; see
[data placement](data/README.md).

From the repository root, create `.env` **only if it does not already exist**:

```sh
cp .env.example .env
```

Replace both secret placeholders. Defaults: `LOG_LEVEL=INFO`, `APP_PORT=8000`.
Docker must be on PATH, or supply `DOCKER=/path/to/docker`; Make also supports
Docker Desktop's bundled executable on macOS.

```sh
make dev
make check
make test
make ingest ARGS=--dry-run
make ingest
make ingest                  # Repeating identical input should create nothing
make reindex
```

`make dev` builds, migrates and starts Django's **development** server at
`http://localhost:8000`. Database state persists in a named volume.

| Command | Purpose |
|---|---|
| `make check` | Django configuration and model/migration consistency |
| `make benchmark` | Warm service comparison; writes ignored `artifacts/search-benchmark.json` |
| `make health` | API/database readiness; unavailable DB returns HTTP 503 |
| `make openapi` | Export live schema to ignored `artifacts/openapi.json` |
| `make api-test` | Optional live HTTP checks; [Bruno setup](tools/bruno/README.md) |
| `make logs` | Follow long-lived API/database container logs |
| `make status` / `make stop` | Inspect / stop services without deleting data |
| `make dev-all` | Start API/database and the optional Docker frontend |

Dry-run counts mean *would create*. Invalid input, duplicate IDs or conflicting
content/provenance abort the import; identical records are unchanged.
Partial searchable patents are retained; blank/canceled-only passages are omitted
from derived data, while raw JSON and positions are preserved.
[Data policy](docs/decisions/002-data-policy.md).

`make reindex` derives one English `tsvector` per patent from title (A),
abstract/claims (B), and usable descriptions (D); a GIN index supports term lookup.
Rebuild explicitly after ingestion: new patents have a null vector until then.
Direct text edits also require rebuilding; there is no automatic freshness
detector or concurrent ingestion/rebuild protocol.

Reproduce read-only discovery separately (Python 3.9+; no dependencies):

```sh
python3 backend/scripts/profile_dataset.py data/raw
```

PostgreSQL has no published host port; the API binds to loopback without
authentication. Health checks database connectivity, not index readiness.
Source data is read-only. Do not use `down -v`: it deletes persisted database data.
Optional editor setup and logging details: [backend guide](backend/README.md).

### Search examples

After ingestion and rebuilding, open `http://localhost:8000/api/docs` or run
(adjust the port if using `APP_PORT`):

```sh
curl --get http://localhost:8000/api/v1/patents/search \
  --data-urlencode 'query=wheel spoke' \
  --data-urlencode 'classification_prefix=B60B' \
  --data-urlencode 'title_keywords=wheel' \
  --data-urlencode 'limit=5'

curl --get http://localhost:8000/api/v1/patents/search \
  --data-urlencode 'title_exact=spoke'
```

All constraints combine with AND. Query lexemes also combine with AND, using
English stemming and no raw query operators. Title/abstract
keywords are literal tokens (repeat parameters for multiple terms). Exact titles
ignore case and collapsed whitespace. Stop-word-only queries return 422.
Pagination defaults to limit 20 / offset 0, with limit 1–100.

Responses contain pre-pagination counts, effective filters, scores and unmodified
excerpts with source positions. An excerpt may explain only part of a cross-field
query. Filter-only scores and classification-only excerpts are null.
Database failures return a sanitized 503. [Full contract](docs/decisions/001-search-contract.md).

## Tests and measured results

`make test` runs PostgreSQL-backed fixtures, including ingestion rollback,
index freshness, SQL-reference ranking, filters, provenance and HTTP errors.
It does not require the supplied dataset. The current **71-test suite** also
covers linked-view counts, date filters and a concurrent-update snapshot test.
The [journal](docs/journal/README.md) records ingestion, PoC and API v1 verification.
The original PoC run predates the v1 refactor.

| Check | Observed result |
|---|---|
| Discovery | 64 JSON files, 640 unique patent IDs, 0 duplicates |
| First ingestion | 640 patents; 10,450 claim + 21,221 description passages |
| Skipped passage entries | 20,819 blank; 128 standalone canceled markers |
| Repeat ingestion | 640 unchanged; 0 new patents or passages |
| Search index | 640 non-null patent vectors; GIN migration applied |
| Correctness | 71 domain/HTTP/benchmark/logging/health/OpenAPI/docs tests pass |
| HTTP collection | 9 requests and 10 Bruno script tests pass |
| Frontend integration | 4 Vitest/jsdom tests pass with synthetic HTTP responses |
| Live frontend | Browser workflow/race checks pass on 640 patents; [timings](docs/benchmarks/003-linked-interface.md) |

All 119 patents lacking usable descriptions are retained.

Recorded runtime and dependency pins: [backend guide](backend/README.md).

### Filtered/unfiltered service benchmark

Reproduce after ingestion and rebuilding:

```sh
make benchmark
```

On 640 patents / 31,671 passages, using 3 warmups and 20 measured calls per
variant, alternating order, limit 20 and warm caches:

| Query | Added filter | Matches without → with | p50 ms without → with |
|---|---|---:|---:|
| `wheel spoke` | Classification `B60B` | 114 → 98 | 124.975 → 146.207 |
| `pneumatic tire` | Classification `B60C` | 169 → 158 | 136.037 → 132.775 |
| `wheel` | Title token `wheel` | 417 → 163 | 140.051 → 144.832 |
| `pressure` | Abstract token `pressure` | 215 → 29 | 110.399 → 103.944 |

These are sequential service-call timings on an Apple M1 host (8 CPUs, 8 GiB;
Docker VM about 3.82 GiB), excluding HTTP and serialization. Filters had mixed
latency effects; fewer candidates do not guarantee faster excerpt selection.
This is not a load test or large-scale capacity claim.
[Methodology, environment, results and limitations](docs/benchmarks/002-search-ranking-fix.md)
include a versioned raw JSON snapshot. New runs write only to ignored
`artifacts/search-benchmark.json`; they do not overwrite that baseline.
Those timings predate the API v1/exploration refactor and do not measure `/explore`.

## Part 2 — Scale design and PoC

The [AWS design](docs/architecture/part-2-aws.md) separates Fargate API tasks
from on-demand ingestion, with RDS PostgreSQL and immutable sources in S3.
It covers bounded batches, durable import status, retries, networking and backups
as proposed work. The target is 10 million patents, not demonstrated capacity.

The [cost model](docs/architecture/part-2-costs.md) budgets about $1,120/month
Single-AZ or $1,966 with one RDS standby, before 20% contingency. These are
assumption-based estimates, not expenses or validated instance sizing.
The [container PoC](docs/architecture/part-2-poc.md) includes exact isolated
Compose commands and recorded results: 640 patents indexed, idempotent reimport
and HTTP checks from image code. No AWS deployment is required by this PoC.

## Part 3 — Interface at Scale

Selected to let reviewers narrow a result set without losing context between
views. The approved design is a results list, classification drill-down and weekly
timeline sharing filters and counts, with stale-response protection.

After the Part 1 setup (API running, sample ingested and index rebuilt):

```sh
make frontend-install
make frontend-dev
```

Requires Node.js 22.12+ and npm. Open `http://127.0.0.1:5173`.
[Frontend commands and proxy details](frontend/README.md).

Alternatively, run the frontend in Docker without installing Node on the host:

```sh
make dev-all
```

Open the same URL. Stop local Vite first to free port 5173, or use
`make dev-all FRONTEND_PORT=5174` and open `http://127.0.0.1:5174`.
First startup downloads the Node image and installs locked npm dependencies.
The frontend uses a separate dependency volume; PostgreSQL data is unchanged.
`make frontend-docker-test` runs Vitest in the running container.
`make frontend-docker-stop` stops only that frontend; `make stop` stops all
Compose services. Host-run Vite still requires Ctrl+C in its terminal.
This runs Vite for local development, not production hosting.

The frontend consumes `/api/v1/patents/explore`. Results, classification
drill-down and a selectable weekly distribution share filters and one response.
Click a classification, week or result-card metadata button to filter all views.
Active filters are individually removable; new queries keep the other filters.
Advanced filters include inclusive date bounds and title/abstract constraints.
All API counts share one PostgreSQL snapshot. Source week is a source-batch date,
not a verified legal filing date.

After the Part 1 setup, try the endpoint independently:

```sh
curl --get http://localhost:8000/api/v1/patents/explore \
  --data-urlencode 'query=wheel spoke' \
  --data-urlencode 'source_week_from=2024-02-15' \
  --data-urlencode 'source_week_to=2024-03-28' \
  --data-urlencode 'limit=5'
```

Omit query/filters to browse all patents. Counts cover all filtered matches,
not only the page. [Exploration contract](docs/decisions/005-enhancement.md).
The live sample has 640 patents in 64 source weeks; existing `wheel spoke`
counts remain 114 (55 with classification `B60B` and title token `wheel`).
The client clears old views during loading, cancels superseded requests and
rejects older successes/errors by request ID, even if cancellation is ignored.
Browser regressions cover these races, linked counts, filters, paging and
loading/empty/error/retry behavior.
`make frontend-unit-test` also runs four fast Vitest/jsdom integration tests
with synthetic API responses, without starting any servers.

Reproduce browser checks and timings:

```sh
make frontend-build
make frontend-preview
# Another terminal, API and preview running:
make frontend-test
```

Requires Python 3 and local `agent-browser`; [setup](frontend/README.md).
On **640 patents / 64 source weeks**, selecting `B60B` from browse
(298 matches, 20 rendered results) took **50.0 ms median / 51.3 ms p95**:
20 warm updates after 3 warmups, local production bundle, headless Chrome 155,
Apple M1 / 8 GB Mac. Timing starts in the filter handler and ends at the second
animation frame after linked-view commit, including API and a paint opportunity.
This is not a remote-network or at-scale benchmark.
[Method and raw measurements](docs/benchmarks/003-linked-interface.md).

At 10 million patents, the interface would need server-side indexed filtering
and aggregation over the same result set, bounded pagination and evidence work,
and a request-versioning contract to keep all views consistent. These are design
requirements, not implemented optimizations.

## Limitations and submission checklist

- Lexical English matching can miss paraphrases. Weights are heuristics; no
  relevance evaluation or legal novelty assessment was performed.
- Python metadata scans, whole-sample ingestion and full index rebuilds are sample-scale.
  Vectors require explicit rebuilding; PostgreSQL full-text size/position limits
  matter for long documents.
- Code and tests have been pushed to the GitHub repository. To complete submission,
  record an accessible ~2-minute walkthrough of Parts 2 and 3, add its link here,
  and publish any final documentation changes.

Optional evidence: [architecture](docs/architecture/README.md),
[benchmarks](docs/benchmarks/README.md), [decisions](docs/decisions/README.md),
[engineering journal](docs/journal/README.md).
