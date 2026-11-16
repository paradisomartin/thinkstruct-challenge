# 01 — Decision Log

Use one short decision record per meaningful choice. Prefer a few high-impact records over logging every implementation detail.

**Status values:** Proposed · Accepted · Rejected · Superseded

## D-001 — Search input/output contract

- **Status:** Accepted (2026-11-16)
- **Approval:** User explicitly confirmed the contract and incomplete-data rules before schema/ingestion implementation.
- **Context:** The challenge allows broad freedom in choosing search inputs and result types.
- **Proposal:** Plain-text query + optional hybrid filters; return ranked patent-level results with metadata and a traceable excerpt. See the concrete draft contract below.
- **Why:** Useful to patent reviewers, simple to validate, and keeps the MVP narrow.
- **Alternatives:** Claim-to-claim retrieval; entire-patent input; claim-level results.
- **Trade-off:** Patent-level ranking can obscure individual claim relevance unless excerpts explain the match.
- **Evidence:** 640 patents inspected on 2026-11-16; 119 have no usable descriptions, and repeated titles cover 183 records. Claims include fragments and canceled ranges. See Milestone 1 in `02-build-journal.md`.
- **Validation remaining:** Excerpt quality and filter/ranking correctness require retrieval tests; acceptance of the contract is not evidence of an implemented search engine.

### Accepted contract (search not implemented yet)

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

- **Status:** Accepted (2026-11-16)
- **Approval:** User explicitly confirmed retaining partial searchable patents, ignoring blank/canceled-only passages, and reporting identity conflicts without overwrite.
- **Question:** Which fields are essential to index a patent? What should happen if claims, descriptions, abstract, or classification are absent?
- **Constraint:** The task requires the choice to be documented.
- **Proposal:** Keep records with a usable string document number and meaningful text in at least one searchable field; optional metadata is nullable. Retain patents without descriptions, skip blank passage entries in the derived index, and preserve original source indices and raw files. Exclude standalone canceled-claim markers from evidence/retrieval, not passages merely mentioning cancellation.
- **Rationale / trade-off:** Avoid losing 119 otherwise searchable patents; requires explicit field-level fallback rather than rejecting every incomplete record.
- **Malformed/conflicting input:** Report or quarantine invalid IDs/no-text records. If future duplicate IDs appear, report conflicts rather than silently overwrite; a version/deduplication rule needs evidence.
- **Evidence:** No top-level missing fields or duplicate IDs observed; 20,819 blank description entries and 168 claim entries containing `cancel`. Marker detection must be tested before implementation; the marker count is not an exclusion count.
- **Implementation policy:** Fail the whole small-sample ingest on the first malformed record or identity conflict, reporting file/position where available. An identical record at the same provenance is unchanged, not a conflict. No silent overwrite, partial import, or quarantine infrastructure.
- **Validation remaining:** Test normalization, atomic rollback, and repeat-ingest behavior before indexing.

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

- **Status:** Superseded by D-008 (2026-11-16); previously Accepted
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
- **AWS candidate, not an accepted deployment design:** static hosting/CDN; ECS Fargate for API/one-off ingestion; RDS PostgreSQL; S3 for sources. Use an appropriate production WSGI/ASGI server for the selected application framework; do not persist PostgreSQL data in ephemeral API containers.
- **Caveat:** Fargate manages compute, not database/index performance. Millions-of-patents capacity, workload, and costs require sizing and measurements. No provisioning authorized or performed.
- **Next gate:** D-001/D-002 were subsequently explicitly accepted. Part 3 enhancement and Part 2 PoC remain unselected.

## D-008 — Django and Django Ninja over Flask

- **Status:** Accepted (2026-11-16)
- **Approval:** User explicitly chose Django and Django Ninja because of recent hands-on familiarity, acknowledging that Flask might be more proportionate to the challenge's small scope.
- **Decision:** Django + Django Ninja API + PostgreSQL native full-text search, with Docker Compose locally. Use Django models/migrations for the schema and a management command for ingestion. Keep retrieval and filter logic independent of HTTP.
- **Alternative:** Flask remains a sensible lighter choice for a small search API; it was the previously accepted direction in D-004.
- **Rationale:** Optimize for the implementer's actual familiarity, not only minimum framework size. Django provides a familiar ORM/migration workflow; Ninja provides typed request/response schemas and OpenAPI documentation.
- **Trade-offs:** More framework structure and configuration than Flask. Familiarity is user-reported; no productivity improvement, performance gain, or implementation result has been measured.
- **Scope:** No user accounts, custom administration UI, queue, or semantic model. Starlight, React, Celery/Redis, and AWS deployment remain deferred under D-007. D-001/D-002 subsequently accepted explicitly.
- **Version policy (Proposed):** Use compatible, supported stable releases; prefer LTS where offered and compatible. Do not assume every dependency has an LTS channel. Pin resolved dependencies and container versions rather than use `latest`; validate exact versions before selecting them.
- **Validation / next:** Docker installation is being handled by the user after the automated attempt failed on interactive sudo. Verify Docker Engine and Compose, confirm remaining contract/data-policy rules, then test schema/migrations and ingestion incrementally. No Django/Ninja packages or containers installed by this change.
- **History:** Explicitly supersedes D-004; PostgreSQL lexical retrieval in D-003 remains unchanged.

## D-009 — Monorepo boundaries and domain-oriented backend

- **Status:** Accepted (2026-11-16)
- **Approval:** User requested a monorepo organized from the outset around root `backend/` and `frontend/` boundaries, with API/services/models separation.
- **Decision:** `backend/config/` holds Django settings. `backend/patents/` is a Django domain app with `models.py`, `services/`, `management/commands/`, `migrations/`, and tests. Add `patents/api/` with Ninja routes/schemas when HTTP search starts. `frontend/README.md` marks the deferred frontend; no frontend dependencies.
- **Why / alternatives:** Prefer one domain app with internal layers over global `api/`, `services/`, and `models/` directories that mix future domains. Keep a two-model `models.py` instead of splitting prematurely.
- **Responsibility rule:** API/commands adapt inputs and errors; services coordinate business use cases and transactions; models express persistence/relationships/constraints. Models are not a substitute for the service layer.
- **Data model:** One patent row preserves source metadata and raw JSON; meaningful claim/description passages are separate rows keyed uniquely by patent, source field, and original index. Blank/canceled-only text remains auditable in raw JSON, not eligible passage evidence.
- **Trade-offs:** Raw JSON duplicates some normalized text storage but preserves exactly what was received. Small-sample ingestion validates in memory and writes in one transaction; not a streaming/concurrent production ingest design.
- **Verification:** Migration consistency, PostgreSQL-backed ingestion tests, actual dataset counts, and repeat ingestion; record actual outcomes in the journal.

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
