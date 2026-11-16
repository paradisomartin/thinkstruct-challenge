# D-011 — First lexical search configuration

**Status:** Accepted; index/rebuild/API tested, sample benchmark recorded · **Date:** 2026-11-16.
User explicitly accepted this baseline before requesting developer workflow tools.

- One persisted `tsvector` per patent plus GIN index. Use nullable-safe title/
  abstract and meaningful passage rows, not unfiltered raw JSON; preserve evidence.
- Explicit `english` configuration on documents/queries for stemming/stop words.
  Based on inspected English examples, not verified language detection of all records.
- `plainto_tsquery`: AND across remaining lexemes anywhere in the patent.
  No operators/automatic OR fallback. Reject a nonblank query reduced to no lexemes.
- Initial labels: title A, abstract/claims B, descriptions D, native weights and
  `ts_rank` defaults. A heuristic to validate, not measured relevance optimization.
- All [D-001](001-search-contract.md) constraints before pagination. Literal keyword
  filters remain separate from stemming. Descending rank then document number.
- Explicit index rebuild command after ingestion; document/test freshness.
  GIN does not automatically maintain a separately derived vector. No worker.

**Why / trade-off:** Simple patent-level counts/pagination. AND can miss partial
matches; long documents affect relevance/position limits. Weights do not repair
extraction artifacts.
**Alternative:** Passage indexing plus patent aggregation offers more local
evidence but complicates counts/ranking/pagination and cross-passage queries;
defer until baseline queries demonstrate need.

**Verification:** Deterministic ranking/cross-field/filter/title/stop-word/missing-
description/pagination/no-match fixtures; index freshness and traceable excerpts.
Inspect real queries; measure filtered/unfiltered latency separately.
Index verification: [checkpoint](../journal/05-search-index.md). Warm sample latency:
[baseline report](../benchmarks/001-search-baseline.md). No relevance evaluation
or at-scale performance validation yet.
