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
| Search service | [Filters, ranking and evidence](06-search-service.md) |
| Search API | [HTTP contract and Bruno tests](07-search-api.md) |
| Search measurements | [Reproducible baseline](08-search-benchmark.md) |
| Ranking regression | [Independent score checks and corrected baseline](09-ranking-regression.md) |
| AWS proposal | [Architecture and approximate costs](10-aws-design-costs.md) |
| Part 2 PoC | [Isolated container ingestion](11-container-ingestion-poc.md) |
| Frontend workspace | [Vite, React and TypeScript setup](12-react-workspace.md) |

Documentation was consolidated from seven starter files in commit `e605994`,
then explicitly split into indexed decision/checkpoint folders at user request.
The authoritative PDF and dataset fingerprint remain unchanged.
Initial snapshot `ae5e302`, ingestion `f8ce343`, and consolidation `e605994`
were published to `origin/main`; newer local changes are not implied published.

## Delivery checklist

- [x] Dataset discovery, accepted contract/data policy, verified ingestion
- [x] Local health/OpenAPI, stage logging, Make workflow and automated tests
- [x] Search/evidence/filter correctness and local measured latency comparison
- [x] Part 2 architecture/cost assumptions and one designated PoC
- [ ] Exactly one Part 3 enhancement and its validation
- [ ] Final reproducible README and accessible ~2-minute Part 2/3 video

**Next:** Implement the selected Part 3 Interface at Scale enhancement from the
initialized React workspace, then finish reproduction and the Part 2/3 recording.
No complete search UI, AWS deployment or at-scale validation yet.
