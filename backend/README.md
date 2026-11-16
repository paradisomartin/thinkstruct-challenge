# Backend

Run Compose commands from the repository root; see the root README for setup.

```text
backend/
  config/                 Django settings; HTTP wiring comes later
  patents/                Django app for the patent domain
    models.py             Persistence, relationships, database constraints
    migrations/           Versioned database schema
    services/             Ingestion and future search use cases; no HTTP dependency
    management/commands/  Thin CLI adapters to services
    tests.py              Ingestion tests against PostgreSQL
  manage.py
  scripts/profile_dataset.py  Standalone, read-only discovery; not a draft
  Dockerfile
  requirements.in         Explicit direct dependency choices
  requirements.lock       Resolved exact runtime versions
```

When HTTP search is implemented, add `patents/api/` for Django Ninja routes,
request/response schemas, and HTTP error mapping. Routes call services; services
use models. Do not create empty API layers or global cross-domain `models/`
and `services/` folders in advance.

Keep two models in `models.py`; split into a `models/` package only when size
justifies it, preserving Django model discovery and migrations.
