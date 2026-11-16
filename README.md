# Thinkstruct — Patent Search

**Goal:** Help a reviewer find vehicle-related patent applications using text
and classification/title/abstract filters, with ranked patents and traceable excerpts.
See the [original brief](docs/reference/thinkstruct-coding-task.pdf) and
[accepted contract](docs/decisions/001-search-contract.md).

**Status:** Dataset discovery, schema, and repeatable PostgreSQL ingestion verified.
Local health/OpenAPI endpoints are available. Search and the required enhancement
are not implemented yet.

## Structure and approach

```text
backend/    Django configuration, patents domain, Dockerfile, dependencies, profiler
frontend/   Deferred frontend boundary; no framework initialized
data/       Ignored local dataset + placement instructions
docs/       Decisions, journal, architecture, authoritative reference PDF
compose.yaml / Makefile / .env.example    Local workflow and configuration
```

Django + Django Ninja was chosen for implementer familiarity; Flask would be
lighter for this scope. PostgreSQL will provide lexical full-text retrieval and
structured filters, not semantic embeddings. [Backend boundaries](backend/README.md).
Compose and one ignored `.env` stay at root; browser configuration, if added later,
must never expose backend secrets.

## Local development

Prerequisites: Make, Docker Engine running, Docker Compose, and the separately supplied
JSON files extracted into `data/raw/`. Data is not published in Git; see
[data placement](data/README.md).

From the repository root, create `.env` **only if it does not already exist**:

```sh
cp .env.example .env
```

Replace both secret placeholders. Optional settings: `LOG_LEVEL=INFO`, `APP_PORT=8000`.
Make handles Docker Desktop's bundled executable on macOS if CLI symlinks are
missing; elsewhere `docker` must be on PATH (or supply `DOCKER=/path/to/docker`).

```sh
make dev
make check
make test
make ingest ARGS=--dry-run
make ingest
make ingest
```

`make dev` builds, starts PostgreSQL, applies committed migrations, and starts
Django's **development** server with reload at `http://localhost:8000` by default.
Backend source is bind-mounted for editing and migration generation.

| Command | Purpose |
|---|---|
| `make migrate` | Build/start DB and apply committed migrations |
| `make makemigrations` | Generate migrations in `backend/`; review before applying |
| `make check` | Django configuration and model/migration consistency |
| `make health` | API/database readiness; unavailable DB returns HTTP 503 |
| `make openapi` | Export live schema to ignored `artifacts/openapi.json` |
| `make logs` | Follow long-lived API/database container logs |
| `make status` / `make stop` | Inspect / stop services without deleting data |

Dry-run counts mean *would create*; migrations must exist first. The second real
ingest must create nothing. Invalid input/duplicate IDs/conflicting existing content
or provenance abort the whole import; identical records are unchanged.
Keep partial searchable patents, omit blank/canceled-only derived passages, and
retain raw JSON and original positions. [Data policy](docs/decisions/002-data-policy.md).

Reproduce read-only discovery separately (Python 3.9+; no dependencies):

```sh
python3 backend/scripts/profile_dataset.py data/raw
```

PostgreSQL has no published host port; source data is mounted read-only.
The API is bound only to host loopback. Its healthcheck tests `SELECT 1`, not
whether the dataset or search index is ready. Database state persists in a named volume.
Do not use `down -v` unless you intend to delete that database.
No production HTTP server or cloud deployment is configured.

### Logs

English application logs explain ingestion stages, counts, dry runs, errors, and
elapsed time; DEBUG adds source-file validation messages. Logs go to stderr;
the ingestion command's final JSON remains on stdout. Application stage logs
do not print patent text or secrets. `make ingest` shows its one-off logs directly;
`make logs` follows the running services. For extra local detail:

```sh
LOG_LEVEL=DEBUG make ingest ARGS=--dry-run
```

### Try the API with Bruno

No user accounts or authentication are configured for this loopback-only MVP.
Ninja generates the contract; do not maintain a separate handwritten OpenAPI spec.

1. Run `make dev`, then `make health` and `make openapi`.
2. In Bruno, choose **Import → OpenAPI** and select `artifacts/openapi.json`.
   Alternatively import `http://localhost:8000/api/openapi.json` by URL.
3. Set the imported collection's server/base URL to `http://localhost:8000`
   (adjust for `APP_PORT`). Paths already contain `/api`; do not add it twice.
4. Send `GET /api/health`; expect `200` and
   `{"status":"ok","database":"ok"}`. Add explicit response assertions in Bruno.

Interactive docs: `http://localhost:8000/api/docs`. Re-export/re-import when new
routes or schemas appear; import is not automatic synchronization or test generation.
No extra template, Bruno CLI install, or committed generated collection is needed yet.
Only health is implemented; search requests will follow. Bruno exercises HTTP;
database integrity/rollback stays covered by `make test`, not direct DB access.
Export and live endpoints were verified; manual Bruno import has not been tested.
[Bruno's import guide](https://docs.usebruno.com/open-api/importOAS).

## Verified results and versions

| Check | Observed result |
|---|---|
| Discovery | 64 JSON files, 640 unique patent IDs, 0 duplicates |
| First ingestion | 640 patents; 10,450 claim + 21,221 description passages |
| Skipped passage entries | 20,819 blank; 128 standalone canceled markers |
| Repeat ingestion | 640 unchanged; 0 new patents or passages |
| Correctness | 19 ingestion/logging/health/OpenAPI/docs tests pass; migrations consistent |

All 119 patents lacking usable descriptions remain retained. Full evidence,
dataset fingerprint, caveats, and learning: [journal](docs/journal/README.md).

Verified runtime: Python **3.13.18**, Django **5.2.19** (LTS series), Ninja **1.8.0**,
psycopg **3.3.9**, PostgreSQL **18.7**. Direct/resolved dependencies are in
`backend/requirements.in` / `backend/requirements.lock`; base image digests are
pinned in the Dockerfile and Compose. Pins still need deliberate security updates.

**Search benchmarks: not run.** Before reporting timings, disclose dataset
fingerprint/size, hardware, query/filters, warm/cold state, timing boundaries,
repetitions, and aggregation (e.g. p50/p95). Compare the same query with/without
filters and verify correctness; filter selectivity alone does not prove a speedup.

## Remaining challenge work

- Part 1: implement search, verify evidence/filter semantics, and compare latency.
- Part 2: complete [architecture](docs/architecture.md), explicit cost assumptions,
  and one designated PoC for ~10 million patents.
- Part 3: select **one** enhancement and meet its exact validation criteria.
- Delivery: add reproducible Part 1/3 commands/results and an accessible ~2-minute
  Part 2/3 screen recording. Demo not yet recorded.

Starlight, React (unless required by the selected enhancement), Celery/Redis,
and live AWS deployment are extras only if time and demonstrated need justify them.
Process and approvals: [decisions](docs/decisions/README.md). D-011 retrieval configuration
is accepted; next implement its index/service/tests before exposing HTTP search.
