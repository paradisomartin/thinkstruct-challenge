# Codex Project Instructions — Thinkstruct Challenge

## Mission

Work with the user to solve the patent-search take-home challenge with an explainable engineering process. The original, authoritative brief is `reference/thinkstruct-coding-task.pdf`. Read it before proposing architecture or code. If these notes differ from the PDF, call out the difference and follow the PDF.

## Collaboration protocol

- Work **incrementally and decision-first**. Start with dataset inspection, then discuss the search contract, retrieval, storage and runtime choices. Do not jump into a finished project before the user approves the high-level plan.
- Before a substantial implementation change, briefly state: goal, alternatives, chosen approach, why, and expected verification. Seek user input at genuinely consequential decisions; otherwise make minimal reversible decisions and document them.
- Explain the **causal model**: what components do, why they exist, how they interact, and the trade-offs. Prefer a small number of clear concepts over unnecessary frameworks.
- Keep output focused and practical. Avoid generating large amounts of boilerplate or infrastructure speculatively.
- Do not invent dataset properties, measured numbers, test outcomes, vendor costs, implementation status, or source references. Label estimates and assumptions.
- Do not run costly external APIs, scraping, downloads, or install extra frameworks without a justified need and user approval.

## Source and scope

- Required fields listed in the brief: Title, Document Number, Abstract, Detailed Description (paragraphs), Claims, Bibtext Citation, Classification Code. Inspect actual shapes and missing data rather than assuming consistent keys.
- The brief gives freedom for choosing search inputs and outputs. Treat current problem statement and solution in notes as **proposals**, not committed requirements.
- Here, the brief's **hybrid search** requirement includes structured filters such as classification-code constraints and title/abstract keywords; it does not automatically require vector plus keyword retrieval.
- Part 1 should include a timed comparison with and without hybrid filters and commentary on efficiency.
- Part 2 needs a readable Markdown architecture, major pipelines, expected costs, failure/status considerations where useful, and a small PoC.
- Part 3 requests **one** enhancement. Pick based on demonstrated value, remaining time, and ability to satisfy the exact acceptance criteria.
- The final README needs actual commands for reproducing Parts 1 and 3 and results, not placeholders. Submission also requires a 2-minute screen recording covering Parts 2 and 3.

## Documentation as part of development

Keep updates concise and grounded in things that happened:

- `notes/00-kickoff.md`: source requirements, scope boundaries, clarified assumptions.
- `notes/01-decision-log.md`: significant decisions with ID, alternatives, rationale, trade-offs, status, evidence. **Do not silently promote Proposed → Accepted.**
- `notes/02-build-journal.md`: dated milestones, obstacles, evidence, resolutions and next step.
- `notes/03-system-design.md`: Part 2 diagram, components, pipelines, failure handling, observed/assumed costs, PoC.
- `notes/04-benchmark-log.md`: actual setup, workload, methodology, baseline and filtered timings, correctness.
- `notes/05-glossary.md`: short terms as they first become relevant, not a generic encyclopedia.
- `notes/06-delivery-checklist.md`: mark only verified completed items.

Prefer readable diffs and a few meaningful records over exhaustive narration. The root README is the evaluator-facing entrance, while `notes/` contains the process evidence.

## Dataset & reproducibility

- Dataset files should be placed under `data/raw/`; it is intentionally gitignored.
- At the first checkpoint, inspect: file count, JSON shape, patent count, field presence, duplicate IDs, sample claims/paragraphs, classification format, date information and data quality.
- If the dataset has not been supplied, report the blocker and stop before fabricating sample observations. You may outline possible contracts but cannot validate them.
- Favor a deterministic local workflow with tests and exact commands. Keep secrets and large generated files out of Git.
- Use benchmarks that disclose dataset size, hardware, warm/cold state, query/filters, repetitions and aggregation method. Do not claim speedups until observed.

## Immediate first task

1. Inspect the repository and original brief.
2. Look for data in `data/raw/` (do not assume it exists).
3. Summarize confirmed requirements and unknowns in a short response.
4. If data exists, profile it read-only and document findings in `notes/02-build-journal.md`.
5. Present **two at most** viable search contract/stack directions and recommend one, without implementing yet.
6. Record proposals in `notes/01-decision-log.md`, identify the next decision for the user, then stop at the checkpoint.
