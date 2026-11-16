# D-008 — Django and Django Ninja

**Status:** Accepted · **Date:** 2026-11-16.

User explicitly chose Django/Ninja over Flask because of recent hands-on
familiarity, acknowledging Flask's lighter footprint for this scope.
Django supplies ORM/migrations; Ninja supplies typed HTTP schemas/OpenAPI.
PostgreSQL and Compose remain. Supersedes [D-004](004-flask.md).

**Trade-off:** More framework configuration, fewer unfamiliar tools. No measured
productivity/performance improvement claimed; no users/custom admin scope added.

Use compatible supported stable releases, LTS where offered, and exact
dependency/image pins with deliberate security updates. Verified versions:
[root README](../../README.md). Ingestion, indexing and the search API are
implemented and covered by PostgreSQL-backed tests.
