# 00 — Kickoff

**Project:** Thinkstruct Patent Search Coding Challenge  
**Status:** Discovery / planning  
**Source of requirements:** `thinkstruct-coding-task.pdf`

## Problem statement

Build a useful search engine over the supplied vehicle patent application data. Search should help a reviewer discover relevant patents and inspect the evidence for each match (especially claims and descriptions). Demonstrate hybrid search, document how the approach could scale to millions of patents, and implement one selected enhancement.

> This is an initial interpretation of the brief, not a final product specification.

## What the challenge explicitly asks for

### Part 1 — Search engine
- Choose and document inputs and outputs.
- Search the provided patent JSON data.
- Support hybrid constraints: classification-code constraints, keywords in the title or abstract, and exact/specific title lookup.
- Compare search runtimes with and without hybrid conditions, and discuss performance.
- Document how records with missing fields are handled.

### Part 2 — At-scale design
- Describe components, pipelines, errors/observability, scaling challenges, and expected costs for ~10 million patents.
- Provide a simple architecture proposal an intern could start implementing.
- Build one narrow proof of concept for a component of that proposal.

### Part 3 — One enhancement
Choose **one** from the brief: evaluation/training, two-phase search, efficiency/large data, machine translation, or interface at scale.

### Delivery
- Publicly accessible/reviewable GitHub repository link.
- Short ~2-minute screen recording explaining Parts 2 and 3.
- README explaining the chosen problem, solution/enhancement, and reproducible setup/run instructions for Parts 1 and 3.

## First decisions, in order

1. **Inspect the dataset** — size, fields, examples, missing values, text lengths, unique IDs, file dates.
2. **Choose the user scenario** — who searches, why, and what makes a result useful.
3. **Choose the search contract** — query and optional filters in; ranked results and evidence out.
4. **Choose retrieval strategy** — lexical, semantic, or a deliberately staged approach.
5. **Choose stack and data storage** — simplest reproducible setup that supports filters and measurement.
6. **Choose missing-data policy** — exclude or include partial patent records with a defined fallback.
7. **Choose one enhancement** — commit to it before building optional features.
8. **Choose Part 2 proof of concept** — just one production-style component to demonstrate.
9. **Define validation and measurements** — functional cases, hybrid-vs-unfiltered timings, relevant UX metrics if applicable.
10. **Plan submission** — README, design notes, decision log, reproducible commands, demo video.

## Proposed, not yet approved, scope

**User story:** A patent reviewer enters a query and optional classification/title/abstract filters, then explores ranked vehicle patents and their most relevant claims or passages.

**MVP input:** free-text query plus optional classification prefix, title/abstract keyword, and title filter.  
**MVP output:** ranked patent-level results with document number, title, classification, citation/abstract where present, and a relevant excerpt.

This is a practical default to evaluate after seeing the data. The original brief intentionally leaves search inputs and outputs open.

## Scope guardrails

- Deliver a working end-to-end search path before pursuing sophisticated relevance or UI polish.
- Document **why** decisions were made, not every keystroke.
- Avoid external scraping unless needed for the chosen search contract.
- Favor transparent benchmarks over unsupported claims about performance.

## Known unknowns / blockers

- Dataset discovery is complete; the same data is now verified in `data/raw/`. See `02-build-journal.md`.
- The local project location is known; the remote repository URL is needed before publishing.
- Flask + PostgreSQL + Docker Compose is the selected backend-first stack. Detailed contract/data-policy approval, Part 3 enhancement, and Part 2 PoC selection remain open.

## Next checkpoint

**After discovery:** establish safe version control, confirm contract/data policy, then implement and verify the smallest ingestion/search path. Documentation UI and unnecessary infrastructure are optional extras, not prerequisites.
