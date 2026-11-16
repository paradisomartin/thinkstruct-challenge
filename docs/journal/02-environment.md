# Stack, version control, and environment · 2026-11-16

- Read the authoritative four-page brief. Specific Part 3 says **pick 1** despite
  overview wording "one or two"; follow the specific instruction. Hybrid means
  structured filters, not necessarily vectors plus keywords.
- Initialized version control and excluded raw data, secrets and generated output.
- Flask/PostgreSQL was initially accepted, then explicitly superseded by
  Django/Ninja for user familiarity. No productivity/performance advantage measured.
  D-001/D-002 accepted before ingestion.
- Local runtime uses Docker Compose; Make supports Docker Desktop's bundled CLI
  when it is not on PATH. This affects command portability, not search behaviour.
- At this checkpoint, frontend work, Part 3 and the Part 2 PoC were deferred.
  Later selections are recorded in [PoC verification](11-container-ingestion-poc.md)
  and [React setup](12-react-workspace.md).
