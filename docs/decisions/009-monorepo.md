# D-009 — Domain-oriented monorepo

**Status:** Accepted · **Date:** 2026-11-16.

User requested root backend/frontend boundaries and layered responsibilities.
The initial layout used Django `config/` plus a domain-local `patents/` app for
API adapters/schemas, services, models, migrations and tests. The HTTP placement
was subsequently superseded by the approved centralized boundary below.

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

The initially approved default keeps Node/npm on the host for Vite; Django and
PostgreSQL stay in Compose. Host `frontend-*` Make targets remain available and
`make dev` continues to start only the backend.

The user subsequently approved an optional Node development container:
`make dev-all` enables Compose profile `frontend`. It uses a digest-pinned Node 26
image, non-root user, source bind mount, isolated `frontend_node_modules` volume
and `/api` proxy to `app:8000`. Startup refreshes dependencies with `npm ci`;
the trade-off is registry access/startup time instead of stale dependency volumes.
Host and container modes can use different published ports.

Stop host Vite before reinstalling host dependencies. Container installations are
isolated from host `node_modules`. `make stop` stops all Compose services;
`make frontend-docker-stop` stops only the Docker frontend. Production static
hosting remains a separate decision; no production Vite deployment is proposed.
