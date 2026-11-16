# Thinkstruct — Patent Search Coding Challenge

> **Status:** Dataset discovery and PostgreSQL ingestion verified. Search and HTTP API are not implemented yet.

## Quick start

1. Read the [original challenge PDF](reference/thinkstruct-coding-task.pdf).
2. Read the [kickoff and requirements](notes/00-kickoff.md) and [decision log](notes/01-decision-log.md).
3. Obtain the separately supplied dataset and extract the JSON files into `data/raw/`. The local copy is present there; dataset contents are excluded from Git.
4. Reproduce discovery from the project root: `python3 backend/scripts/profile_dataset.py data/raw` (Python 3.9+; standard library only).
5. Read the [discovery evidence](notes/02-build-journal.md) and [decisions](notes/01-decision-log.md) before implementation. Persistent instructions are in [`AGENTS.md`](AGENTS.md).

## Selected direction and sequence

- **Backend first:** Django + Django Ninja API + PostgreSQL native full-text search, run locally with Docker Compose. Chosen for the implementer's familiarity; Flask would be a lighter alternative for this scope. See D-008. No semantic model or queue initially.
- **Completed checkpoint:** contract/data policy accepted; schema and repeatable ingestion verified before search/API expansion.
- **Then:** search correctness, traceable evidence, and timed comparisons with/without filters.
- **Required later:** Part 2 architecture/PoC, one Part 3 enhancement, reproducible delivery.
- **Optional extras after required work:** Astro Starlight documentation, React UI (unless selected for the required enhancement), Celery/Redis only if asynchronous work justifies them, and live AWS deployment.
- **AWS design candidate:** static hosting/CDN, ECS Fargate for API/ingestion tasks, RDS PostgreSQL, S3 source storage. No cloud resources provisioned or scale/cost claims validated.
- **Docker verified:** Engine/CLI 29.9.3 and Compose v5.7.0 respond locally. If Docker Desktop is installed but its CLI is absent from your PATH on macOS, use `export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"`.

## Accepted search scope (not yet implemented)

Search vehicle-related patents using a text query plus optional classification code, title, and abstract constraints; return ranked results with traceable excerpts. Detailed semantics are recorded in D-001.

## Repository layout

```text
backend/    Django config, patents domain, dependency pins, Dockerfile, profiler
frontend/   Deferred frontend boundary; README only
data/       Local ignored dataset + tracked placement instructions
notes/      Engineering journal, decisions, glossary, validation evidence
reference/  Authoritative challenge PDF
diagrams/   Architecture diagram sources/exports when needed
```

See [backend responsibilities](backend/README.md). Compose orchestration stays at
the root; application code lives under `backend/`.

## Milestones and notes

- [00 — Kickoff](notes/00-kickoff.md)
- [01 — Decision log](notes/01-decision-log.md)
- [02 — Build journal](notes/02-build-journal.md)
- [03 — At-scale system design](notes/03-system-design.md)
- [04 — Benchmarks](notes/04-benchmark-log.md)
- [05 — Glossary](notes/05-glossary.md)
- [06 — Delivery checklist](notes/06-delivery-checklist.md)

## Challenge structure

- **Part 1:** Implement basic patent search, including classification/title/abstract constraints and a runtime comparison with/without filters.
- **Part 2:** Propose an at-scale architecture (roughly 10 million patents), costs, and a narrow proof of concept.
- **Part 3:** Select **one** enhancement from the PDF and evaluate it.
- **Submission:** GitHub link; a short (about 2-minute) walkthrough of Parts 2 and 3; reproducible instructions for Parts 1 and 3 in this README.

## Implementation, setup and results

### Ingestion slice

Prerequisites: Docker Engine running, Docker Compose, and supplied JSON files in
`data/raw/`. Run from the repository root:

```sh
cp .env.example .env
```

Replace both placeholder values in `.env` with local secrets. Do not overwrite an
existing `.env`. It is ignored by Git; `.env.example` is tracked.

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

The second real ingest must report unchanged records and create no duplicates.
`--dry-run` validates files and existing database conflicts; `created` and
`passages_created` then mean *would create*. Migrations must exist before a dry run.
Every malformed record or conflicting ID aborts the complete ingest transaction.
Identical content and provenance are skipped. Blank passages and standalone
canceled-claim markers are omitted from passage rows, but retained in raw JSON.

**Observed:** 12 PostgreSQL-backed tests passed. First ingest created **640
patents and 31,671 passages** (10,450 claim entries and 21,221 description entries);
repeat ingest created **0**, with **640 unchanged**. Excluded 20,819 blank entries
and 128 standalone canceled markers. See the journal for evidence and limitations.

The database is not exposed on a host port. Dataset access is a read-only mount,
not part of the application image. A named volume persists PostgreSQL state:

```sh
docker compose stop db
docker compose start db
```

Do not run `down -v` unless you intend to delete that database volume. This setup
is local development only; no HTTP server, production credentials, cloud resources,
search index, or benchmarks are provided.

**Verified runtime:** Python 3.13.18, Django 5.2.19 (5.2 LTS), Django Ninja 1.8.0,
psycopg 3.3.9, PostgreSQL 18.7. Direct dependencies are in
`backend/requirements.in`; resolved exact versions are in
`backend/requirements.lock`. Base image digests are pinned in
`backend/Dockerfile` and `compose.yaml`. Pins need deliberate security updates.
Python 3.9+ is sufficient only for the standalone profiler, not for the backend.

### Search and enhancement

Not implemented. Part 1 search commands, benchmark results, and the selected Part 3
enhancement must be added and verified before submission.

## Demo

**Pending.** Add a shareable link when recorded.
