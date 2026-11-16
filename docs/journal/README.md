# Journal index

Historical checkpoint notes: pending work and test counts describe each
checkpoint, not the current state. Commands/results overview: [root README](../../README.md).
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
| Exploration API | [Versioned HTTP layer and consistent linked counts](13-exploration-api.md) |
| Linked interface | [Live views, request races and browser measurements](14-linked-interface.md) |
| Docker frontend | [Optional development container](15-docker-frontend.md) |
| Figma styling | [Desktop design adaptation](16-figma-desktop.md) |

## Delivery checklist

- [x] Dataset discovery, accepted contract/data policy, verified ingestion
- [x] Local health/OpenAPI, stage logging, Make workflow and automated tests
- [x] Search/evidence/filter correctness and local measured latency comparison
- [x] Part 2 architecture/cost assumptions and one designated PoC
- [x] Exactly one Part 3 enhancement and its sample-scale validation
- [x] Reproduction commands, measured results and implementation/tests pushed
- [ ] Accessible ~2-minute Part 2/3 video linked from the README

**Next:** Record the Part 2/3 walkthrough, add its accessible link and publish
the final documentation changes. The optional Docker frontend and supplied
Figma desktop styling are implemented, not additional challenge requirements.
No AWS deployment or at-scale validation is claimed.
