# Codex Project Instructions — Thinkstruct Challenge

## Mission

Work with the user to solve the patent-search take-home challenge with an explainable engineering process. The original, authoritative brief is `docs/reference/thinkstruct-coding-task.pdf`. Read it before proposing architecture or code. If the documentation differs from the PDF, call out the difference and follow the PDF.

## Collaboration protocol

- Work **incrementally and decision-first**. Start with dataset inspection, then discuss the search contract, retrieval, storage and runtime choices. Do not jump into a finished project before the user approves the high-level plan.
- Before a substantial implementation change, briefly state: goal, alternatives, chosen approach, why, and expected verification. Seek user input at genuinely consequential decisions; otherwise make minimal reversible decisions and document them.
- Explain the **causal model**: what components do, why they exist, how they interact, and the trade-offs. Prefer a small number of clear concepts over unnecessary frameworks.
- Keep output focused and practical. Avoid generating large amounts of boilerplate or infrastructure speculatively.
- Do not invent dataset properties, measured numbers, test outcomes, vendor costs, implementation status, or source references. Label estimates and assumptions.
- Do not run costly external APIs, scraping, downloads, or install extra frameworks without a justified need and user approval.

## Source and scope

- Required fields listed in the brief: Title, Document Number, Abstract, Detailed Description (paragraphs), Claims, Bibtext Citation, Classification Code. Inspect actual shapes and missing data rather than assuming consistent keys.
- The brief gives freedom for choosing search inputs and outputs. Follow explicitly accepted records indexed in `docs/decisions/README.md`; do not treat remaining proposals as committed requirements.
- Here, the brief's **hybrid search** requirement includes structured filters such as classification-code constraints and title/abstract keywords; it does not automatically require vector plus keyword retrieval.
- Part 1 should include a timed comparison with and without hybrid filters and commentary on efficiency.
- Part 2 needs a readable Markdown architecture, major pipelines, expected costs, failure/status considerations where useful, and a small PoC.
- Part 3 requests **one** enhancement. Pick based on demonstrated value, remaining time, and ability to satisfy the exact acceptance criteria.
- The final README needs actual commands for reproducing Parts 1 and 3 and results, not placeholders. Submission also requires a 2-minute screen recording covering Parts 2 and 3.

## Documentation as part of development

Keep updates concise and grounded in things that happened:

- `README.md`: evaluator-facing requirements, exact commands, measured results, benchmark methodology, and delivery links.
- `docs/decisions/`: one record per choice, with a short README index, rationale, alternatives, trade-offs, and evidence. **Do not silently promote Proposed → Accepted.**
- `docs/journal/`: one entry per dated checkpoint, with a short README index/checklist; preserve obstacles, evidence, learning, and next step.
- `docs/architecture.md`: current versus proposed pipelines; Part 2 components, failures, assumptions/costs, and designated PoC.
- `docs/benchmarks/`: indexed experiment reports and selected raw JSON snapshots; fresh runs write to ignored `artifacts/`, never overwrite a committed baseline.
- `docs/reference/`: authoritative brief. Add `docs/assets/` only when diagram files actually exist.

Define relevant concepts in context. Avoid separate kickoff/glossary/benchmark/checklist scaffolding, repeated run instructions, or empty templates. Prefer readable diffs and a few meaningful records over exhaustive narration.

## Dataset & reproducibility

- Dataset files should be placed under `data/raw/`; it is intentionally gitignored.
- At the first checkpoint, inspect: file count, JSON shape, patent count, field presence, duplicate IDs, sample claims/paragraphs, classification format, date information and data quality.
- If the dataset has not been supplied, report the blocker and stop before fabricating sample observations. You may outline possible contracts but cannot validate them.
- Favor a deterministic local workflow with tests and exact commands. Keep secrets and large generated files out of Git.
- Use benchmarks that disclose dataset size, hardware, warm/cold state, query/filters, repetitions and aggregation method. Do not claim speedups until observed.

## Current checkpoint and layout

- Dataset discovery and PostgreSQL ingestion are verified; read `docs/journal/README.md` and the relevant checkpoint entries before continuing.
- D-001/D-002 and the D-011 lexical retrieval configuration are explicitly accepted. Implement search incrementally with correctness tests before benchmarks; do not silently choose the Part 3 enhancement.
- Keep Django code/configuration/dependencies/Dockerfile in `backend/`, organized by domain with thin API/CLI adapters and services. Keep Compose and `.env.example` at root.
- `frontend/` is deferred. No Starlight, React, workers, or AWS deployment unless subsequently justified/approved.
