# D-009 — Domain-oriented monorepo

**Status:** Accepted · **Date:** 2026-11-16.

User requested root backend/frontend boundaries and layered responsibilities.
Use Django `config/` plus a domain-local `patents/` app for API adapters/schemas,
services, models, migrations, and tests. Prefer this over global folders mixing
domains. Two models fit `models.py`; split only when justified.

Services coordinate use cases/transactions; models express persistence/constraints;
HTTP/commands adapt inputs/errors. [Backend layout](../../backend/README.md).

Raw JSON duplicates normalized storage but preserves auditability. Validate the
small sample in memory and write atomically; not a production streaming/concurrent
ingestion design.
