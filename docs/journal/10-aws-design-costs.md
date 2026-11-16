# AWS design and approximate costs · 2026-11-16

- Consolidated architecture under `docs/architecture/`, distinguishing the
  implemented Part 1 local system from the proposed Part 2 AWS system.
- Incorporated the user-edited draw.io diagram and its rendered SVG. The
  proposal keeps lexical PostgreSQL search, separates API and on-demand
  ingestion, and explains networking, access, retries and index readiness.
- Consulted official AWS pricing pages and regional Price List catalogs.
  ECS/RDS/S3 publications are from November 2026, with selected rates effective
  November 1. Other pages are dated by consultation, not assumed publication.
- Added a [cost model](../architecture/part-2-costs.md) for `us-east-1`: about
  $1,120/month Single-AZ or $1,966 with one RDS standby, before 20% contingency.
  Workload, storage and instance sizes are explicit budget assumptions, not
  measurements or an approved deployment configuration.
- Checked calculations, local Markdown links, diagram XML and whitespace.
  Documentation-only work; backend tests were not rerun for this checkpoint.
- No AWS deployment or spend. Part 2 still needs an explicitly verified PoC;
  Part 3 selection and final delivery/video remain pending.
