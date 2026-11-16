# Logs, health, Make, and API testing · 2026-11-16

- **Approval:** D-011 search baseline accepted. User additionally requested English
  logs, quick health, Make tasks, Bruno/OpenAPI, and short indexed documentation.
- **Built:** Stage logging to stderr with separate command JSON stdout; INFO
  summaries and DEBUG per-file validation. No text/secret dumps in stage logs.
  Root Make wraps Compose; local API binds loopback and reloads backend edits.
- **Health:** `/api/health` checks `SELECT 1`, returns 200 or sanitized 503.
  Not proof of dataset/index readiness. Simulated DB-failure test verifies 503
  and no exception details.
- **Verified:** `make dev`, `health`, `openapi`, `check`, `makemigrations`, `test`,
  and dry-run ingestion. **19 tests pass**. Live host HTTP returned 200 for
  health, OpenAPI, and docs. Export matched the live schema; migration directory
  is writable by the container user. Dry run reported 640 unchanged, no new rows.
- **Restart check:** `make stop` followed by `make dev` restored both services
  healthy; health/docs/schema returned 200. SQL verified 640 patents and 31,671
  passages persisted. All local Markdown links resolve after the folder split.
- **Problem/fix:** Initial `/api/docs` returned 500 because the minimal ingestion
  settings omitted a Django template backend. Added that backend and a regression
  test; live docs now return 200. Make initially failed to resolve Docker despite
  PATH export; explicit bundled executable plus helper PATH fixed it.
- **Bruno:** Initially documented OpenAPI import. After user approval, installed
  global CLI 4.3.0 and verified version/help. npm emitted deprecated transitive
  dependency warnings; no additional install-script permissions granted.
  User requested moving their collection from Documents into `tools/bruno/`:
  reviewed four YAML files (only local base URL, no credentials), moved all five
  files with matching hashes, and kept `.DS_Store` ignored.
  CLI smoke returned 200 for one health request, **0 tests/0 assertions**. Reports
  stay ignored under `artifacts/`; `make api-test` wraps the same collection.
  Generated examples are not test results. GUI import not independently tested.
- **Scope:** No users, frontend, search endpoint/index, benchmark, or AWS deployment.
  Next implement D-011 retrieval tests/service. UI waits for a useful search API.
