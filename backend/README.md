# Backend

Run Compose commands from the repository root; see the [root README](../README.md) for setup.

```text
backend/
  config/                 Django settings, HTTP wiring, infrastructure health route
  patents/                Django app for the patent domain
    models.py             Persistence, relationships, database constraints
    migrations/           Versioned database schema
    services/             Ingestion, indexing, search and benchmark use cases
    api.py / schemas.py   Ninja routes, validation and response schemas
    management/commands/  Thin CLI adapters to services
    tests.py              Ingestion/logging tests against PostgreSQL
  manage.py
  scripts/profile_dataset.py  Standalone, read-only dataset discovery
  Dockerfile
  requirements.in         Explicit direct dependency choices
  requirements.lock       Resolved exact runtime versions
```

The health route lives in `config/api.py`, tested in `config/tests.py`.
Patent routes call services, which use models. Search, HTTP and benchmark tests
live in `patents/test_search.py`, `test_api.py` and `test_benchmark.py`.

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
