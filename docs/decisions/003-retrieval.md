# D-003 — Lexical PostgreSQL retrieval

**Status:** Accepted direction; not implemented · **Date:** 2026-11-16.

Use native `tsvector`/`tsquery`, structured constraints before final ranking/limit,
and `ts_rank`/`ts_rank_cd` candidates, not BM25. GIN is an inverted term lookup
index, not a relevance function. Filters establish eligibility; retrieval finds
candidates; ranking orders them; excerpts explain the match.

**Why / trade-off:** Explainable local baseline without model/vector infrastructure;
may miss paraphrases and long descriptions affect ranking.
**Alternative:** Semantic passage embeddings with filtering and patent aggregation,
adding model/splitting/storage/evaluation decisions. SQLite FTS5/BM25 was proposed
earlier but never accepted.

[D-011](011-search-configuration.md) specifies the subsequently accepted baseline.
Correctness and latency remain unmeasured.
