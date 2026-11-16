# D-003 — Lexical PostgreSQL retrieval

**Status:** Accepted direction; implemented via D-011 · **Date:** 2026-11-16.

Use native `tsvector`/`tsquery`, structured constraints before final ranking/limit,
and native ranking, not BM25. D-011 selects `ts_rank` rather than `ts_rank_cd`.
GIN is an inverted term lookup
index, not a relevance function. Filters establish eligibility; retrieval finds
candidates; ranking orders them; excerpts explain the match.

**Why / trade-off:** Explainable local baseline without model/vector infrastructure;
may miss paraphrases and long descriptions affect ranking.
**Alternative:** Semantic passage embeddings with filtering and patent aggregation,
adding model/splitting/storage/evaluation decisions. SQLite FTS5/BM25 was proposed
earlier but never accepted.

[D-011](011-search-configuration.md) specifies the subsequently accepted baseline.
Correctness tests and local warm latency measurements are recorded in the
[corrected baseline](../benchmarks/002-search-ranking-fix.md); relevance quality
and large-scale capacity remain unmeasured.
