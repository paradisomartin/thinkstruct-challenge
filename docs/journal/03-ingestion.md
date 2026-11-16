# Milestone 2 — Schema and ingestion · 2026-11-16

- **Built:** Domain-oriented Django monorepo, patent/passage models, migration,
  ingestion service/command, Docker image and root Compose.
- **Versions:** Python 3.13.18, PostgreSQL 18.7, Django 5.2.19 LTS, Ninja 1.8.0,
  psycopg 3.3.9. Checked [Django](https://www.djangoproject.com/download/),
  [Ninja](https://pypi.org/pypi/django-ninja/json),
  [psycopg](https://pypi.org/pypi/psycopg/json) and official image manifests.
  Exact dependencies/base digests pinned; updates remain deliberate.
- **Verified:** Initial **12 tests pass**, including malformed/partial input,
  provenance, marker handling, duplicate IDs, rollback, dry run, repeat ingestion.
  Migration applied; drift check found no changes.
- **Real import:** 640 patents / 31,671 passages: **10,450 claims + 21,221 descriptions**.
  Excluded 20,819 blank entries and **128 standalone canceled markers**.
  Dry-run plan matched; second ingest created 0 patents/0 passages and reported
  640 unchanged. Independent SQL counts matched. All 119 patents without usable
  descriptions retained.
- **Learning:** 168 entries containing `cancel` is not the 128 whole-entry markers;
  neither measures canceled legal claims. Idempotency means identical repeated
  input has no new effect.
- **Trade-off:** Raw JSON duplicates storage to preserve auditability; in-memory
  validation and one transaction suit this sample, not an unmeasured production
  streaming/concurrent pipeline. Dataset read-only; named database volume persists.
- **Checkpoint:** Commit `f8ce343`; search was not implemented.
