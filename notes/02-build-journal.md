# 02 — Build Journal

Keep short, chronological milestones. Record observations and evidence, not a keystroke transcript.

## Milestone 0 — Brief review

- **Goal:** Understand the assignment and define the boundaries of the solution.
- **Actions:** Read the four-page challenge brief; separated core search, at-scale design/PoC, and one optional enhancement.
- **Findings:** The brief allows choosing search input/output. It explicitly requires hybrid filters, timing commentary, handling of incomplete fields, scaling considerations, a GitHub submission, and a ~2-minute walkthrough.
- **Blockers:** Dataset ZIP not yet supplied in this conversation.
- **Next:** Inspect the ZIP and decide the query/result contract.

## Milestone 1 — Dataset discovery — 2026-11-16

**Status:** Discovery completed for the supplied sample; proposals await approval. No search engine implemented.

### Scope, obstacles, and resolution

- Read `AGENTS.md`, the four-page authoritative PDF, `README.md`, and every Markdown file under `notes/`.
- `data/raw/` does not exist. However, the supplied data is present in `data/patent_data_small/`. Inspected that location read-only; no need to supply another copy and no files moved.
- The README, kickoff, and `data/README.md` contain stale starter statements about absent data. This entry supersedes those statements for discovery.
- This project directory is not currently a Git repository (`git status --short` failed). No `.gitignore` is present at the root; the starter's claim that raw data is ignored is not verified. Resolve before any future commit; do not assume the supplied data is protected.
- The PDF's overview says "one or two" enhancements, but its specific Part 3 heading says "pick 1"; follow the specific instruction. Hybrid search requires structured constraints, not necessarily vectors plus keywords.

### Reproduction and evidence

Run from the project root:

```sh
python3 scripts/profile_dataset.py data/patent_data_small
```

The standard-library-only profiler prints JSON to stdout and does not write to the dataset. Files are sorted by relative path. Its dataset fingerprint is SHA-256 over UTF-8 lines of `relative_path<TAB>file_sha256<NEWLINE>`:

```text
94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6
```

Observed runtime: Python 3.9.6, SQLite 3.54.0. Two profile calls returned identical reports; assertions checked record count, unique IDs, blank-only descriptions, and classification totals. An in-memory FTS5 virtual table could be created: this checks local capability only, not retrieval correctness or performance. No dependencies installed, external APIs called, search benchmarks run, or relevance measurements made.

### Inventory and actual schema

- **64 JSON files**, each a top-level array containing **10 objects**: **640 patent records**, **15,939,070 bytes** in total.
- All files parsed successfully; no non-object entries observed.
- Every record has exactly the same eight keys below. All have **0 missing keys, 0 null values, and 0 empty top-level values (0/640, 0%)**. Nested empty strings require a separate check.

| Key | Observed type | Minimum / median / maximum length |
|---|---|---|
| `title` | string | 4 / 36 / 162 characters |
| `doc_number` | string | 11 / 11 / 11 characters |
| `filename` | string | 28 / 28 / 28 characters |
| `abstract` | string | 62 / 714 / 1,768 characters |
| `detailed_description` | list of strings | 1 / 47 / 677 entries |
| `claims` | list of strings | 1 / 19 / 46 entries |
| `bibtex` | string | 141 / 173 / 299 characters |
| `classification` | string | 9 / 10 / 11 characters |

These are actual lowercase keys, not the human-readable labels in the PDF. `bibtex` contains a citation string; citation correctness has not been independently validated.

### Identity and dates

- **640 unique `doc_number` values; 0 duplicate IDs** across all files. All are strings of 11 digits; preserve string identity.
- **43 repeated-title groups cover 183 records**. A title is not an identifier; exact-title lookup must allow multiple results.
- JSON filename dates span **2024-02-15 to 2025-05-01**. XML filenames have the same date range and matching document numbers in all 640 cases.
- XML kind codes: **636 `A1`, 4 `A9`**. Do not assume `A1` when constructing provenance links or identifiers.
- No explicit date keys exist. The PDF describes the JSON filename date as a filing week, but filenames alone do not establish a legal filing date. Preserve as `source_batch_date` if needed, not a verified `filing_date`.

### Classifications

- One string per record, **145 distinct values**, all matching the observed textual pattern `B60[A-Z][0-9]+FI`.
- Examples: `B60B104FI`, `B60C25138FI`. This pattern describes the supplied strings, not a verified classification standard or a general validation rule.
- Four-character prefixes: **B60B: 298; B60C: 318; B60D: 20; B60F: 1; B60G: 1; B60J: 1; B60R: 1**.
- Preserve original codes; do not invent separators or infer a CPC/IPC/FI interpretation from the suffix.
- A `B60B` filter retains 298/640 patents. This establishes dataset selectivity, **not** a latency improvement.

### Claims, descriptions, and quality

- **Claims:** 10,578 string entries; none blank. Nonblank entry length: 5 / 200 / 4,829 characters (min / median / max).
- **168 claim entries contain `cancel`**, including `1 - 5 . (canceled)`. This is a text-marker count, not a count of legally canceled claims.
- Entries are not guaranteed complete or individually numbered claims: the first `SPOKE` entry begins `an axle body, having a middle segment...`; another short entry is `a semicircular plate (`. Numbered entries and canceled ranges coexist. Array positions must not be presented as legal claim numbers; do not attempt speculative reconstruction.
- **Descriptions:** 42,040 string entries; **20,819 blank (49.52%)**, leaving **21,221 nonblank passages**.
- **616/640 patents (96.25%)** have at least one blank description entry; **119/640 (18.59%)** have no usable description text despite a nonempty list. Example: `20240051339`, `PNEUMATIC TIRE`, `detailed_description: [""]`.
- Nonblank description length: 2 / 463 / 25,013 characters. Uneven length matters for ranking and any future passage splitting.
- Formatting artifacts appear in inspected text, e.g. `FIG.1is` and `insert100according`. No measured artifact rate or text-repair effectiveness is claimed.

Representative record, abridged directly from `patents_ipa240215.json`, array index 0:

```text
doc_number: "20240051333"
title: "SPOKE"
classification: "B60B104FI"
filename: "US20240051333A1-20240215.XML"
claims: 10 entries; first begins "an axle body, having a middle segment..."
detailed_description: 15 entries; index 1 is blank
description index 0 begins: "The present disclosure will now be described more specifically..."
```

The profiler prints further excerpt samples with original zero-based source indices.

### Implications and next checkpoint

- **Mental model:** filters decide eligibility; retrieval finds and ranks text matches; excerpts provide traceable evidence. These are separate responsibilities.
- Keep patents without descriptions rather than losing 119 otherwise searchable records. Skip blank passages in a derived index, preserving raw text and source positions. Treat canceled-only markers separately from meaningful evidence.
- Long descriptions can dominate or dilute patent-level lexical scoring. Start with an explainable baseline, then inspect representative query results before adding weighting or passage-level retrieval.
- D-001 through D-004 now contain concrete **Proposed**, not accepted, contracts and stack/data-policy choices. No Part 2 or Part 3 implementation started.
- **Next joint decision:** approve or revise the patent-level contract and local lexical-first direction. Then confirm the missing-content policy before implementing ingestion/search. Stop here for user review.

---

## Post-discovery checkpoint — Stack discussion and version control — 2026-11-16

- **User consultation:** Reviewed search contract, ingestion, identity/provenance, retrieval versus ranking, structured hybrid filters, result granularity, and correctness versus latency. User asked about Starlight + React, Flask/PostgreSQL containers, optional Celery/Redis, and AWS Fargate.
- **Agreed direction:** Backend-first Flask + PostgreSQL + Docker Compose; lexical native PostgreSQL search instead of the previously proposed SQLite/BM25 baseline. D-003/D-004 are explicitly Accepted at the directional level. Detailed D-001/D-002 remain Proposed.
- **Why:** A single metadata/search database and familiar deployment concepts support the user's full-stack/AWS goals. This adds setup relative to SQLite, not a demonstrated performance benefit.
- **Scope discipline:** Starlight/React presentation, queues, and live AWS deployment are extras only after required work, unless a UI is explicitly selected as the required Part 3 enhancement. No Part 3 choice made. Keep the Markdown journal as source documentation.
- **AWS mental model:** Fargate runs containers; RDS persists database state; S3 stores source objects. A queue is justified by asynchronous work, not by the word "scale." No cloud provisioning, costs, or capacity guarantees established.
- **Location change observed:** During this checkpoint `data/patent_data_small/` was no longer present and `data/raw/` contained the JSON files. This session did not move them. Reprofiled `data/raw/`: 64 files, 640 records, identical discovery fingerprint `94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6`. Earlier location statements above are historical.
- **Version control:** Initialized local Git on `main`. Added `.gitignore` for dataset contents, environment secrets, Python artifacts, local databases, and generated files; keep `data/README.md` tracked. `git check-ignore` verified exclusions for raw data, `.env` files, `.DS_Store`, virtual environments, and local PostgreSQL storage.
- **Tooling blocker:** `docker` is not found on PATH. `psql` exists at `/opt/homebrew/bin/psql`; this does not prove that a PostgreSQL server is running. No packages installed or containers started.
- **Next:** Review/stage the documentation snapshot and create the initial commit. Remote URL is still required for push. Enable Docker/Compose before container verification, then confirm contract/data policy and implement schema/ingestion incrementally.

## Milestone template

### Milestone N — Title
- **Goal:**
- **Actions:**
- **Findings:**
- **Problem / diagnosis:**
- **Outcome:**
- **Verification:**
- **Next:**
