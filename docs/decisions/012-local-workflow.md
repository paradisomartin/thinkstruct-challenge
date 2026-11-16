# D-012 — Observable local API workflow

**Status:** Accepted · **Date:** 2026-11-16.
User requested English logs, healthcheck, Make shortcuts, and Bruno from generated
Ninja OpenAPI, without users/authentication initially.

- Standard-library logs: INFO stage counts/durations, DEBUG source-file validation,
  ERROR failures. No patent text, queries, credentials, or raw DB exceptions in
  application stage logs. stderr remains separate from ingestion JSON stdout.
  Durations are diagnostics, not search benchmarks.
- `GET /api/health`: `SELECT 1`, HTTP 200/sanitized 503, Compose readiness.
  Not dataset/index readiness or pure process liveness; successful probes DEBUG.
- Make wraps Compose, not replaces it. `dev` applies committed migrations;
  generation is explicit/reviewed. Logs/status/stop/check/test/export stay simple.
- API binds host loopback; writable backend mount supports reload/migrations.
  Dataset mount stays read-only. Django development server is not production.
- Ninja owns `/api/openapi.json`; Bruno imports file/URL without another manual
  contract/template/CLI dependency. Re-import on changes; add assertions yourself.
  Bruno checks HTTP, not database integrity.

**Trade-off:** Useful development HTTP before search, no frontend/worker/cloud
scope. Health/OpenAPI/docs and PostgreSQL tests are verified; manual Bruno import
is not. [Workflow evidence](../journal/04-local-workflow.md).
