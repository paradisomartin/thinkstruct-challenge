# D-010 — Documentation and configuration boundaries

**Status:** Accepted · **Date:** 2026-11-16.

Keep the README as the reviewer entry point. Indexed decision, journal,
architecture and benchmark folders hold optional rationale and evidence without
turning the README into a development log.

Selected benchmarks pair a numbered report with a raw JSON snapshot.
Fresh runs write to ignored `artifacts/`, preserving historical evidence.

Compose and `.env.example` remain at root because orchestration crosses services;
backend owns Dockerfile/dependencies. One ignored local `.env` suffices. Frontend
variables cannot contain backend secrets.
