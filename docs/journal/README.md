# Journal index

One entry per checkpoint; do not append unrelated milestones to old entries.
Commands/results overview: [root README](../../README.md).
Approvals: [decisions](../decisions/README.md).

| Checkpoint (2026-11-16) | Evidence |
|---|---|
| 1 | [Dataset discovery](01-dataset-discovery.md) |
| Setup | [Stack, Git, Docker](02-environment.md) |
| 2 | [Schema and ingestion](03-ingestion.md) |
| Local workflow | [Logs, health, Make, OpenAPI](04-local-workflow.md) |
| Search index | [Persisted vectors and explicit rebuild](05-search-index.md) |

Documentation was consolidated from seven starter files in commit `e605994`,
then explicitly split into indexed decision/checkpoint folders at user request.
The authoritative PDF and dataset fingerprint remain unchanged.
Initial snapshot `ae5e302`, ingestion `f8ce343`, and consolidation `e605994`
were published to `origin/main`; newer local changes are not implied published.

## Delivery checklist

- [x] Dataset discovery, accepted contract/data policy, verified ingestion
- [x] Local health/OpenAPI, stage logging, Make workflow and automated tests
- [ ] Search/evidence/filter correctness and measured latency comparison
- [ ] Part 2 architecture/cost assumptions and one designated PoC
- [ ] Exactly one Part 3 enhancement and its validation
- [ ] Final reproducible README and accessible ~2-minute Part 2/3 video

**Next:** Implement D-011 search service, filters and evidence with deterministic tests.
No search endpoints, search benchmarks, frontend, or at-scale validation yet.
