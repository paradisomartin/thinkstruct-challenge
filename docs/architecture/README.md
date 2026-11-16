# Architecture

Start with the implemented local system, then the AWS proposal. The PoC verifies
one local slice of that proposal; the cost model supplies its budget assumptions.

| Document | Scope | Status |
|---|---|---|
| [Part 1 — Local architecture](part-1-local.md) | Ingestion, indexing and search on Docker Compose / PostgreSQL | Implemented on the supplied sample |
| [Part 2 — AWS architecture](part-2-aws.md) | Search and ingestion flows for a larger patent corpus | Proposed; not deployed or capacity-tested |
| [Part 2 — Approximate costs](part-2-costs.md) | November 2026 AWS rates, budget assumptions and Single-AZ / Multi-AZ scenarios | Estimate, not measured capacity |
| [Part 2 — Container ingestion PoC](part-2-poc.md) | Disposable jobs, isolated PostgreSQL and search from the built image | Verified locally on the supplied sample |

Part 3's implemented React views and consistency contract are described in
[D-005](../decisions/005-enhancement.md); reproduction is in the
[frontend guide](../../frontend/README.md), with
[browser measurements](../benchmarks/003-linked-interface.md).

The AWS proposal includes an [editable draw.io diagram](diagrams/architecture.drawio)
and its [SVG preview](diagrams/architecture.svg).

No AWS resources are deployed. Capacity at ten million patents requires
representative query, ingestion and index-sizing measurements.
