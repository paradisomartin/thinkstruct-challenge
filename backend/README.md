# Backend

Run Compose commands from the repository root; see the [root README](../README.md) for setup.

```text
backend/
  config/                 Django settings, URL mounting and WSGI
  api/
    api.py                Ninja composition and unversioned health route
    v1/patents/
      api.py              Versioned search/explore routes and HTTP error mapping
      schemas.py          Request/response contracts
    tests/                HTTP, serialization and generated OpenAPI tests
  patents/                Django app for the patent domain
    models/               Patent and Passage; exports preserve patents.models imports
    migrations/           Versioned database schema
    services/             Ingestion, indexing, search and benchmark use cases
    management/commands/  Thin CLI adapters to services
    tests/                Ingestion, indexing, search, exploration and benchmark tests
  manage.py
  scripts/profile_dataset.py  Standalone, read-only dataset discovery
  Dockerfile
  requirements.in         Explicit direct dependency choices
  requirements.lock       Resolved exact runtime versions
```

`config/urls.py` mounts Ninja under `/api/`. Patent routes are versioned:
`/api/v1/patents/search` and `/api/v1/patents/explore`. Health remains at
`/api/health`; OpenAPI/docs remain at `/api/openapi.json` and `/api/docs`.
Old unversioned patent routes are not aliases.

Routes call domain services; no HTTP schemas or framework behavior belong in
models. Run `make test` for both test packages (`patents` and `api`).
Exploration uses `TransactionTestCase` because its service owns a read-only,
repeatable-read transaction; it must be called outside an existing transaction.
The model split preserves tables and migrations.

Recorded runtime: Python 3.13.18, Django 5.2.19 (LTS series), Django Ninja 1.8.0,
psycopg 3.3.9 and PostgreSQL 18.7. Direct dependencies are in `requirements.in`,
resolved versions in `requirements.lock`; Dockerfile/Compose pin base image
digests. Updates require deliberate compatibility and security review.

## Optional editor environment

Docker contains the runtime dependencies. For host-side Python analysis only,
run `make venv` from the root with Python 3.13 installed (or pass
`PYTHON=/path/to/python3.13`). Select `.venv/bin/python` in your editor and add
`backend/` to its analysis path if needed. The target installs
`backend/requirements.lock` and does not replace an existing environment.
Continue running application/tests through Compose; the host environment does
not inherit its database connection settings.

## Development commands and logs

`make migrate` applies committed migrations. `make makemigrations` generates
schema changes in the bind-mounted backend; review them before applying.
Neither is necessary as a separate step when reproducing the root quick start.

Application stage logs go to stderr; command JSON stays on stdout.
INFO logs summarize counts and elapsed time; DEBUG adds source-file validation:

```sh
LOG_LEVEL=DEBUG make ingest ARGS=--dry-run
```

Stage logs omit patent text, query text and credentials. Django's development
HTTP access logs are separate and can contain request URLs.
