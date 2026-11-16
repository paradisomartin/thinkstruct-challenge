# React workspace · 2026-11-16

- User approved Interface at Scale as the primary Part 3 enhancement, followed
  by Vite + React + TypeScript in the existing `frontend/` boundary.
- Initialized a minimal setup screen, strict TypeScript, pinned dependencies
  and npm lockfile. No UI framework, Astro, Starlight or second backend.
- Added a loopback-only Vite development server on port 5173 with `/api` proxy
  to the existing Django API on port 8000. Production routing remains unconfigured.
- Verified `npm install`, `npm ci` and `npm run build` (including TypeScript).
  npm reported zero known vulnerabilities at installation time; npm ci warned
  about an unapproved optional `fsevents` install script, without failing.
- HTTP smoke checks returned 200 for the page, transformed React entry point,
  proxied health and proxied OpenAPI. No browser rendering, interaction or
  accessibility test is claimed. Backend tests were not rerun for this scaffold.
- Next: agree on the linked-view API/state contract, verify available date and
  classification semantics, then implement consistent counts and stale-response
  protection before measuring interactions.
