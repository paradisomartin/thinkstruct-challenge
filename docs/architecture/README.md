# Architecture

Start with the local system, then read the AWS proposal. The two documents
separate what runs today from what still needs to be built and validated.

| Document | Scope | Status |
|---|---|---|
| [Part 1 — Local architecture](part-1-local.md) | Ingestion, indexing and search on Docker Compose / PostgreSQL | Implemented on the supplied sample |
| [Part 2 — AWS architecture](part-2-aws.md) | Search and ingestion flows for a larger patent corpus | Proposed; not deployed or capacity-tested |
| [Part 2 — Approximate costs](part-2-costs.md) | November 2026 AWS rates, budget assumptions and Single-AZ / Multi-AZ scenarios | Estimate, not measured capacity |

The AWS proposal includes an [editable draw.io diagram](diagrams/architecture.drawio)
and its [SVG preview](diagrams/architecture.svg).

The cost document supplies explicit working assumptions, not approved production
requirements. Refine them with representative measurements and select/verify the
Part 2 PoC explicitly. Neither pricing nor the diagram proves that the proposed
system can handle ten million patents.
