# Thinkstruct — Patent Search Coding Challenge

> **Status:** Dataset discovery complete; backend-first stack selected. Search, API, and containers are not implemented yet.

## Quick start

1. Read the [original challenge PDF](reference/thinkstruct-coding-task.pdf).
2. Read the [kickoff and requirements](notes/00-kickoff.md) and [decision log](notes/01-decision-log.md).
3. Obtain the separately supplied dataset and extract the JSON files into `data/raw/`. The local copy is present there; dataset contents are excluded from Git.
4. Reproduce discovery from the project root: `python3 scripts/profile_dataset.py data/raw` (Python 3.9+; standard library only).
5. Read the [discovery evidence](notes/02-build-journal.md) and [decisions](notes/01-decision-log.md) before implementation. Persistent instructions are in [`AGENTS.md`](AGENTS.md).

## Selected direction and sequence

- **Backend first:** Flask API + PostgreSQL native full-text search, run locally with Docker Compose. No semantic model or queue initially.
- **Next checkpoint:** confirm remaining contract/data-policy details, then validate a minimal database schema and ingestion before search/API expansion.
- **Then:** search correctness, traceable evidence, and timed comparisons with/without filters.
- **Required later:** Part 2 architecture/PoC, one Part 3 enhancement, reproducible delivery.
- **Optional extras after required work:** Astro Starlight documentation, React UI (unless selected for the required enhancement), Celery/Redis only if asynchronous work justifies them, and live AWS deployment.
- **AWS design candidate:** static hosting/CDN, ECS Fargate for API/ingestion tasks, RDS PostgreSQL, S3 source storage. No cloud resources provisioned or scale/cost claims validated.
- **Current setup blocker:** `docker` is not on the local PATH; a working Docker/Compose environment is needed before container verification.

## Working hypothesis (not yet approved)

Search vehicle-related patents using a text query plus optional classification code, title, and abstract constraints; return ranked results with useful excerpts. Validate this scope after profiling the dataset.

## Milestones and notes

- [00 — Kickoff](notes/00-kickoff.md)
- [01 — Decision log](notes/01-decision-log.md)
- [02 — Build journal](notes/02-build-journal.md)
- [03 — At-scale system design](notes/03-system-design.md)
- [04 — Benchmarks](notes/04-benchmark-log.md)
- [05 — Glossary](notes/05-glossary.md)
- [06 — Delivery checklist](notes/06-delivery-checklist.md)

## Challenge structure

- **Part 1:** Implement basic patent search, including classification/title/abstract constraints and a runtime comparison with/without filters.
- **Part 2:** Propose an at-scale architecture (roughly 10 million patents), costs, and a narrow proof of concept.
- **Part 3:** Select **one** enhancement from the PDF and evaluate it.
- **Submission:** GitHub link; a short (about 2-minute) walkthrough of Parts 2 and 3; reproducible instructions for Parts 1 and 3 in this README.

## Implementation, setup and results

**Not implemented yet.** Replace this section after the MVP and selected enhancement are built. Include exact dependency installation, data preparation, run/test/benchmark commands, sample queries, measured results and any prerequisites or secrets (without committing secrets).

## Demo

**Pending.** Add a shareable link when recorded.
