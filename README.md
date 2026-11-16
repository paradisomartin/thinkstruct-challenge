# Thinkstruct — Patent Search

**Goal:** Help a reviewer find vehicle-related patent applications using text
and classification/title/abstract filters, with ranked patents and traceable excerpts.
See the [original brief](docs/reference/thinkstruct-coding-task.pdf) and
[accepted contract](docs/decisions.md).

**Status:** Dataset discovery, schema, and repeatable PostgreSQL ingestion verified.
Search, HTTP API, and the required enhancement are not implemented yet.

## Structure and approach

```text
backend/    Django configuration, patents domain, Dockerfile, dependencies, profiler
frontend/   Deferred frontend boundary; no framework initialized
data/       Ignored local dataset + placement instructions
docs/       Decisions, journal, architecture, authoritative reference PDF
compose.yaml / .env.example    Local orchestration and configuration example
```

Django + Django Ninja was chosen for implementer familiarity; Flask would be
lighter for this scope. PostgreSQL will provide lexical full-text retrieval and
structured filters, not semantic embeddings. [Backend boundaries](backend/README.md).
Compose and one ignored `.env` stay at root; browser configuration, if added later,
must never expose backend secrets.

## Run the ingestion slice

Prerequisites: Docker Engine running, Docker Compose, and the separately supplied
JSON files extracted into `data/raw/`. Data is not published in Git; see
[data placement](data/README.md).

From the repository root, create `.env` **only if it does not already exist**:

```sh
cp .env.example .env
```

Replace both placeholders with local secrets. If Docker Desktop is installed on
macOS but `docker` is not on PATH:

```sh
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

```sh
docker compose build app
docker compose up -d --wait db
docker compose run --rm app python manage.py check
docker compose run --rm app python manage.py migrate
docker compose run --rm app python manage.py makemigrations --check --dry-run
docker compose run --rm app python manage.py test patents
docker compose run --rm app python manage.py ingest_patents /data/raw --dry-run
docker compose run --rm app python manage.py ingest_patents /data/raw
docker compose run --rm app python manage.py ingest_patents /data/raw
```

Dry-run counts mean *would create*; migrations must exist first. The second real
ingest must create nothing. Invalid input/duplicate IDs/conflicting existing content
or provenance abort the whole import; identical records are unchanged.
Keep partial searchable patents, omit blank/canceled-only derived passages, and
retain raw JSON and original positions. [Data policy](docs/decisions.md).

Reproduce read-only discovery separately (Python 3.9+; no dependencies):

```sh
python3 backend/scripts/profile_dataset.py data/raw
```

PostgreSQL has no published host port; source data is mounted read-only.
Its named volume persists across `docker compose stop db` / `docker compose start db`.
Do not use `down -v` unless you intend to delete that database.
No production HTTP server or cloud deployment is configured.

## Verified results and versions

| Check | Observed result |
|---|---|
| Discovery | 64 JSON files, 640 unique patent IDs, 0 duplicates |
| First ingestion | 640 patents; 10,450 claim + 21,221 description passages |
| Skipped passage entries | 20,819 blank; 128 standalone canceled markers |
| Repeat ingestion | 640 unchanged; 0 new patents or passages |
| Correctness | 12 PostgreSQL-backed ingestion tests pass; migrations consistent |

All 119 patents lacking usable descriptions remain retained. Full evidence,
dataset fingerprint, caveats, and learning: [journal](docs/journal.md).

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
Process and approvals: [decisions](docs/decisions.md). Next checkpoint:
agree on lexical retrieval configuration before implementing search.
