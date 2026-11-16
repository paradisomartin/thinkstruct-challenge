# Engineering decisions

The [challenge brief](reference/thinkstruct-coding-task.pdf) is authoritative.
Statuses: **Proposed**, **Accepted**, **Rejected**, **Superseded**.
Decisions below were discussed on 2026-11-16; acceptance does not imply implementation.

## D-001 — Search contract · Accepted

**Why:** Patent-level results with traceable passages keep the reviewer workflow
small and explainable. Claim-only results are an alternative, but source entries
are not reliably complete or numbered legal claims.

| Input | Semantics |
|---|---|
| `query` | Plain text over title, abstract, usable claims/descriptions; no raw SQL/FTS syntax or promise of semantic understanding. |
| `classification_prefix` | Optional uppercase prefix of the original code, e.g. `B60B`. |
| `title_keywords` | Optional literal terms; all must occur as normalized title tokens. |
| `abstract_keywords` | Optional literal terms; all must occur as normalized abstract tokens. |
| `title_exact` | Whole-title equality after case folding, trimming, and whitespace collapse. Multiple patents may match. |
| `limit`, `offset` | Defaults 20 and 0; limit 1–100, offset nonnegative. |

Combine filters with AND. Keyword normalization uses case folding and Unicode
alphanumeric tokens, without stemming or substrings; each term must normalize
to one token. Retrieval tokenization is separate and will be documented when built.
A missing filtered field fails the constraint.

Allow filter-only requests, ordered by `doc_number`; reject requests without
effective text or filters and invalid parameters. Query results sort by relevance,
then `doc_number` for stable ties. No matches returns an empty list.

**Output:** `results`, pre-pagination `total_matches`, and effective request.
Each result has document number, title, original classification, nullable
abstract/citation, score and ranking method (null score for filter-only lookup),
and provenance (`source_file`, zero-based `record_index`).
An excerpt contains original text, source field, and original zero-based array
index (null for scalar fields), or is null if unavailable. Prefer matching
meaningful claims/descriptions, then matching title/abstract. Never invent
passage evidence from a metadata-only match.

**Boundaries:** Scores are not probabilities or legal assessments. Array positions
are not legal claim numbers. No arbitrary-ID scraping, verified filing-date filter,
or novelty determination. Excerpt window size remains to be validated.
**Approval:** User explicitly confirmed this contract before ingestion.

## D-002 — Partial records and identity conflicts · Accepted

Keep a usable nonblank string ID and meaningful text in at least one searchable
field. Optional metadata may be null. Retain patents without descriptions;
ignore blank passages and standalone canceled-claim markers in derived evidence,
but preserve raw JSON and original positions. Do not discard text merely mentioning
cancellation.

**Why:** Rejecting empty descriptions would lose 119 otherwise searchable patents.
**Trade-off:** Requires field-level fallbacks rather than blanket rejection.
**Conflict policy:** Abort the complete small-sample import on malformed input or
duplicate input IDs. Existing identical content and provenance are unchanged;
changed content/provenance is an error, never an overwrite. No quarantine service.
**Evidence:** 12 ingestion tests; 640 records retained and repeat ingestion creates
none. User explicitly approved these rules. See [journal](journal.md).

## D-003 — Lexical PostgreSQL retrieval · Accepted direction; not implemented

Use native `tsvector`/`tsquery` search and structured constraints before final
ranking/limit. Candidate ranking functions are `ts_rank`/`ts_rank_cd`; these are
not BM25. A GIN inverted index maps terms to eligible rows; it does not define
relevance. Filters establish eligibility; retrieval finds candidates; ranking
orders them; excerpts explain the match.

**Why:** Explainable local baseline without model downloads or vector infrastructure.
**Trade-off:** May miss paraphrases; long descriptions affect ranking.
**Alternative:** Local semantic passage embeddings with metadata filtering and
patent aggregation; adds model, splitting, storage, and evaluation decisions.
SQLite FTS5/BM25 was proposed earlier but never accepted.
**Next gate:** Choose retrieval configuration and verify correctness/latency;
no relevance or speedup results yet.

## D-004 — Flask stack · Superseded by D-008

Originally accepted Flask + PostgreSQL + Compose. Flask could be more proportionate
for a small API, but familiarity motivated the explicit switch below.

## D-008 — Django + Django Ninja · Accepted

Django supplies ORM and schema migrations; Ninja will supply typed HTTP schemas
and OpenAPI. PostgreSQL and Compose remain. The user chose this over Flask because
of recent hands-on familiarity, not measured productivity or performance.

**Trade-off:** More framework structure than Flask; fewer unfamiliar tools for
the implementer. No users, custom admin UI, or authentication scope added.
**Versions:** Use compatible supported stable releases, LTS where offered, and
exact dependency/image pins. Verified versions are in the root README; pins
still require deliberate security updates. Backend implemented; HTTP layer deferred.

## D-007 — Backend-first scope and AWS boundary · Accepted

Required ingestion/search/measurements and challenge deliverables precede extras.
Starlight, React, Celery/Redis, and live AWS deployment are deferred. A React UI
becomes required only if Interface at Scale is explicitly chosen for Part 3.
Queues need demonstrated asynchronous work; retries and duplicate execution add
complexity. Initial ingestion is a command, not a background worker.

AWS candidate: static hosting/CDN, ECS Fargate API/ingest tasks, RDS PostgreSQL,
S3 sources. Fargate manages compute, not index/query performance. Production needs
an appropriate WSGI/ASGI server and persistent database storage, not API-container
files. No resources provisioned; no capacity or cost guarantees.

## D-009 — Domain-oriented monorepo · Accepted

Root `backend/` and `frontend/` boundaries; Django `config/` and `patents/` app
inside the backend. Domain-local API adapters/schemas, services, models, migrations,
and tests instead of global folders mixing domains. Two models fit `models.py`;
split only when justified. [Backend layout](../backend/README.md).

Services coordinate use cases/transactions; models express persistence and
constraints; HTTP/commands are adapters. Raw JSON plus normalized passage rows
duplicates storage but preserves auditability. Validate this small sample in
memory and write atomically; not a production streaming/concurrent ingestion design.

## D-010 — Documentation and configuration boundaries · Accepted

User approved one `docs/` area: this log, journal, architecture, reference PDF,
and assets only when diagrams exist. README owns run commands, results, benchmark
methodology, and delivery requirements. Definitions appear in context instead
of a separate glossary. Preserve meaningful evidence/history, remove starter
templates and repetition.

Compose and `.env.example` remain at root because orchestration crosses services;
the backend Dockerfile/dependencies stay in `backend/`. One ignored local `.env`
is enough now. Add frontend environment examples only when needed; browser-exposed
values must never contain backend secrets. No extra `project/` nesting.

## Open choices

- **D-005 · Part 3 enhancement · Proposed:** Interface at Scale or Two-phase Search;
  choose exactly one based on value, acceptance criteria, and remaining time.
- **D-006 · Part 2 PoC · Proposed:** Select one narrow component explicitly.
  Local Compose/ingestion exists but has not been designated or evaluated as that PoC.
