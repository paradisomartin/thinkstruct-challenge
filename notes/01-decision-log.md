# 01 — Decision Log

Use one short decision record per meaningful choice. Prefer a few high-impact records over logging every implementation detail.

**Status values:** Proposed · Accepted · Rejected · Superseded

## D-001 — Search input/output contract

- **Status:** Proposed
- **Context:** The challenge allows broad freedom in choosing search inputs and result types.
- **Proposal:** Plain-text query + optional hybrid filters; return ranked patent-level results with metadata and a traceable excerpt. See the concrete draft contract below.
- **Why:** Useful to patent reviewers, simple to validate, and keeps the MVP narrow.
- **Alternatives:** Claim-to-claim retrieval; entire-patent input; claim-level results.
- **Trade-off:** Patent-level ranking can obscure individual claim relevance unless excerpts explain the match.
- **Evidence:** 640 patents inspected on 2026-11-16; 119 have no usable descriptions, and repeated titles cover 183 records. Claims include fragments and canceled ranges. See Milestone 1 in `02-build-journal.md`.
- **Acceptance gate:** User approval of result granularity and filter semantics; excerpt quality still requires retrieval validation.

### Draft contract (Proposed, not implemented)

**Input**

| Field | Proposed semantics |
|---|---|
| `query` | Plain text, not raw SQL or FTS syntax. Search title, abstract, usable claims, and descriptions. No promise of semantic understanding. |
| `classification_prefix` | Optional uppercase prefix of the original classification string, e.g. `B60B`. |
| `title_keywords` | Optional list of literal terms; all must occur as normalized tokens in the title. |
| `abstract_keywords` | Optional list of literal terms; all must occur as normalized tokens in the abstract. |
| `title_exact` | Optional whole-title equality after case folding, trimming, and whitespace collapse; not a unique-ID lookup. |
| `limit`, `offset` | Proposed defaults 20 and 0; limit 1–100, offset nonnegative. |

Combine active filters with AND. Keyword normalization uses case folding and Unicode alphanumeric tokens, without stemming or substring matching; terms must normalize to a single token. A missing filtered field fails that constraint. Query retrieval tokenization is separate and must be documented when implemented.

Allow query-free requests if at least one effective filter exists, enabling specific-title lookup. Reject blank requests without filters and invalid parameters. Filter-only results sort by `doc_number`; text-query results sort by relevance with `doc_number` as a deterministic tie-breaker. No matches returns an empty list.

**Output:** `results` plus `total_matches` before pagination and the effective request. Each result contains:

- `doc_number`, `title`, original `classification`, nullable `abstract` and `bibtex`;
- `score` with a documented ranking method (null for filter-only lookup; not a probability or legal assessment);
- `excerpt`: original text plus `source_field` and zero-based `source_index` for list fields (null for scalar fields), or null when unavailable;
- provenance: `source_file` and zero-based `record_index`.

Prefer a matching meaningful claim/description excerpt when available; fall back to matching title/abstract. Do not fabricate a passage match when only metadata matched. Exact truncation/window size remains an implementation detail to validate. No arbitrary-patent-ID scraping, legal novelty determination, verified filing-date filter, or UI commitment in this contract.

## D-002 — Handling incomplete records

- **Status:** Proposed
- **Question:** Which fields are essential to index a patent? What should happen if claims, descriptions, abstract, or classification are absent?
- **Constraint:** The task requires the choice to be documented.
- **Proposal:** Keep records with a usable string document number and meaningful text in at least one searchable field; optional metadata is nullable. Retain patents without descriptions, skip blank passage entries in the derived index, and preserve original source indices and raw files. Exclude standalone canceled-claim markers from evidence/retrieval, not passages merely mentioning cancellation.
- **Rationale / trade-off:** Avoid losing 119 otherwise searchable patents; requires explicit field-level fallback rather than rejecting every incomplete record.
- **Malformed/conflicting input:** Report or quarantine invalid IDs/no-text records. If future duplicate IDs appear, report conflicts rather than silently overwrite; a version/deduplication rule needs evidence.
- **Evidence:** No top-level missing fields or duplicate IDs observed; 20,819 blank description entries and 168 claim entries containing `cancel`. Marker detection must be tested before implementation; the marker count is not an exclusion count.
- **Acceptance gate:** User approval; test normalization and fallbacks before indexing.

## D-003 — Retrieval and hybrid-filter strategy

- **Status:** Accepted (direction only, 2026-11-16)
- **Approval:** User requested proceeding after the Flask/PostgreSQL recommendation, deferring unnecessary infrastructure.
- **Selected direction — Lexical-first:** PostgreSQL native full-text search over derived patent text alongside metadata and original passage provenance. Apply structured constraints before final ranking/limit; use the same query semantics in filtered and unfiltered comparisons.
- **Alternative approach B — Semantic passages:** Python + a local embedding model over meaningful claims/description passages, SQLite for metadata, and local vector scoring over eligible passages; aggregate to patents with traceable excerpts. Filtering must constrain candidates before the final top-k, not only discard results afterward.
- **Why:** Local baseline without model downloads or vector infrastructure; explainable lexical evidence and structured constraints.
- **Trade-offs:** Lexical search may miss paraphrases; long descriptions affect ranking. PostgreSQL uses `tsvector`/`tsquery`, GIN indexes, and functions such as `ts_rank` or `ts_rank_cd`, not native BM25. Ranking configuration remains to be validated. The semantic alternative adds model selection/download approval, passage splitting, and relevance evaluation.
- **Decision criteria:** Reproducibility, relevance, coding time, filter behavior, and measurable latency.
- **Reminder:** In this task, 'hybrid search' explicitly includes structured classification/title/abstract constraints; don't assume it necessarily means combining vectors and keywords.
- **Evidence / validation:** 640 patents and 21,221 nonblank description passages observed. Only SQLite FTS5 was checked during discovery; PostgreSQL availability and behavior remain unverified. No retrieval-quality or latency claims established.
- **History:** Replaces the unaccepted SQLite FTS5/BM25 proposal following the user's stack discussion.

## D-004 — Technology stack

- **Status:** Accepted (2026-11-16)
- **Approval:** User asked to proceed with the recommended steps after the Flask/PostgreSQL discussion and explicitly deferred Starlight and unnecessary components.
- **Decision:** Python + Flask API + PostgreSQL with Docker Compose for local reproducibility. Start with schema/ingestion and a thin search path; keep the contract independent of HTTP.
- **Why / trade-off:** Familiar full-stack/cloud components and one metadata/search store. More setup than SQLite and unnecessary for capacity at 640 records, but aligned with the user's engineering goals.
- **Decision criteria:** Setup complexity, install time, local machine constraints, portability, and tests.
- **Evidence / validation:** Flask, PostgreSQL, and Compose are not implemented yet. Check tooling, health, persistence, ingestion, and reproducible commands incrementally.
- **History:** Replaces the unaccepted Python/SQLite CLI proposal.

## D-007 — Backend-first scope and AWS boundary

- **Status:** Accepted (scope only, 2026-11-16)
- **Context:** User asked about Starlight, React, Flask/PostgreSQL containers, workers, and AWS Fargate; subsequently requested optional extras only if time remains.
- **Decision:** Core ingestion/search and measurements first; Markdown documentation remains the journal. Astro Starlight, React, Celery/Redis, and live AWS deployment are deferred extras. A React UI may become required only if Interface at Scale is explicitly selected for Part 3.
- **Alternatives / rationale:** Building all infrastructure upfront risks time needed for challenge acceptance criteria. A SQLite CLI is simpler but less aligned with the chosen backend-first goals.
- **Workers:** Add a queue only for demonstrated asynchronous work; retries and duplicate execution add operational complexity. Initial ingestion can be a one-off command.
- **AWS candidate, not an accepted deployment design:** static hosting/CDN; ECS Fargate for API/one-off ingestion; RDS PostgreSQL; S3 for sources. Use a production WSGI server for Flask; do not persist PostgreSQL data in ephemeral API containers.
- **Caveat:** Fargate manages compute, not database/index performance. Millions-of-patents capacity, workload, and costs require sizing and measurements. No provisioning authorized or performed.
- **Next gate:** D-001/D-002 remain Proposed; stack approval does not accept every detailed contract/data rule. Part 3 enhancement and Part 2 PoC remain unselected.

## D-005 — Part 3 enhancement

- **Status:** Pending
- **Candidates:** Interface at Scale (full-stack showcase); Two-phase Search (retrieval-quality showcase).
- **Decision criteria:** Demonstration value, ability to complete acceptance criteria, and remaining time after MVP.
- **Note:** The assignment asks to pick only one enhancement.

## D-006 — Part 2 proof of concept

- **Status:** Pending
- **Question:** Which one narrow production component best supports the chosen architecture?
- **Candidates:** Containerized search service; persistent ingest/index job with status tracking.

---

## Template

### D-XXX — Decision title
- **Status:** Proposed / Accepted / Rejected / Superseded
- **Context:**
- **Decision:**
- **Alternatives:**
- **Rationale:**
- **Trade-offs:**
- **Validation / evidence:**
- **Date:**
