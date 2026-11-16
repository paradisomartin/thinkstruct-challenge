# D-010 — Documentation and configuration boundaries

**Status:** Accepted, organization explicitly refined · **Date:** 2026-11-16.

User first approved one `docs/` area with decisions/journal/architecture and the
reference PDF. Subsequently requested decision and journal folders to avoid
ever-growing files: one decision per record, one journal entry per checkpoint,
each with a short index.

README owns commands, a results summary, and delivery requirements.
User subsequently approved `docs/benchmarks/` for detailed methodology/results:
one numbered report and selected raw JSON snapshot per experiment, a short index,
and links from README/journal. New executions go to ignored `artifacts/` rather
than overwriting the versioned baseline.
Define concepts in context; preserve evidence/history, remove empty templates
and duplicated scaffolding. Assets only when diagrams actually exist.

Compose and `.env.example` remain at root because orchestration crosses services;
backend owns Dockerfile/dependencies. One ignored local `.env` suffices. Frontend
environment examples only when needed; browser variables cannot contain secrets.
No extra `project/` nesting.
