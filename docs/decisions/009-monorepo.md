# D-009 — Domain-oriented monorepo

**Status:** Accepted · **Date:** 2026-11-16.

User requested root backend/frontend boundaries and layered responsibilities.
Use Django `config/` plus a domain-local `patents/` app for API adapters/schemas,
services, models, migrations, and tests. Prefer this over global folders mixing
domains.

The user subsequently approved a centralized HTTP boundary:
`api/api.py` composes Ninja, `api/v1/patents/{api,schemas}.py` defines the v1
contract, and `api/tests/` tests transport behavior. Routes use
`/api/v1/patents/...`; unversioned patent routes are removed rather than aliased.
Health remains outside the domain version at `/api/health`.

Models are split into `patents/models/patent.py` and `passage.py`, exported by
`models/__init__.py` so existing domain imports remain stable. Domain tests live
under `patents/tests/`, separated by use case. This is a module reorganization,
not a database schema change.

Services coordinate use cases/transactions; models express persistence/constraints;
HTTP/commands adapt inputs/errors. [Backend layout](../../backend/README.md).

Raw JSON duplicates normalized storage but preserves auditability. Validate the
small sample in memory and write atomically; not a production streaming/concurrent
ingestion design.

## Frontend development runtime

Keep Node/npm on the host for Vite; Django and PostgreSQL remain in Docker Compose.
The user approved this split after verifying local startup. Root `frontend-*`
Make targets wrap npm, while `make dev` continues to start the backend.

A Node development container would pin the runtime and avoid a host installation,
but adds bind-mount, dependency-volume and network/proxy configuration. Defer it
until needed; the frontend lockfile already pins dependencies. A running Vite
process must be stopped before reinstalling dependencies. Production static
hosting is a separate decision and does not require a long-running Vite server.
