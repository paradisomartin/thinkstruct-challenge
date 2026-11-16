# Optional Docker frontend · 2026-11-16

- User approved optional frontend containerization after the documentation review.
- Added Compose profile `frontend`, digest-pinned Node 26 development image,
  non-root user, source reload and a dependency volume isolated from host npm.
- `make dev-all` starts the backend and frontend; `make dev` remains backend-only.
  `/api` targets `app:8000` inside Docker. Host Vite retains its loopback default.
- Startup runs `npm ci` to reflect lockfile changes. This favors correctness over
  faster offline startup. No production hosting or frontend AWS deployment added.
- Verified Docker startup on host port 5174 without stopping existing host Vite.
  Four Vitest tests pass inside the container; live browser regression groups
  pass against that frontend and the real API. Host TypeScript/build still pass.
- Docker development browser timings are not the production baseline. Existing
  benchmark snapshots are unchanged; new run output remains under `artifacts/`.
- No ingestion, database schema change or deletion of PostgreSQL volumes.
  Part 2's separate PoC profile/volume and reproduction commands remain unchanged.
