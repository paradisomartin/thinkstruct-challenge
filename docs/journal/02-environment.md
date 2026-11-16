# Stack, version control, and environment · 2026-11-16

- Read the authoritative four-page brief. Specific Part 3 says **pick 1** despite
  overview wording "one or two"; follow the specific instruction. Hybrid means
  structured filters, not necessarily vectors plus keywords.
- Git was initially absent; initialized `main`, excluded raw data/secrets, and
  published initial snapshot `ae5e302` using the user's requested repository-local
  author email. Remote: `https://github.com/paradisomartin/thinkstruct-challenge.git`.
- Flask/PostgreSQL was initially accepted, then explicitly superseded by
  Django/Ninja for user familiarity. No productivity/performance advantage measured.
  D-001/D-002 accepted before ingestion.
- Automated Docker install failed on interactive sudo and rolled back; user
  installed manually. Verified CLI/Engine 29.9.3, Desktop 4.99.0, Compose v5.7.0.
  Docker.app executable works despite this session's missing CLI symlink/PATH.
  Make now handles the bundled path and credential helper. MCP Toolkit stays optional.
- Frontend, workers, and AWS deployment are deferred; Part 3 and Part 2 PoC
  remain explicitly unselected.
