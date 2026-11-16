# Search index — 2026-11-16

- Implemented the first D-011 increment: nullable patent `SearchVectorField`,
  GIN migration, indexing service, management command and `make reindex`.
- Explicit English conversion uses title A, abstract/claims B, descriptions D.
  Passage aggregation orders by original source index and uses normalized rows,
  not raw JSON. One atomic SQL update is intentionally sample-sized.
- `make test check reindex` passed: **25 tests**, no migration drift, migration
  applied, **640 patents rebuilt**. Independent SQL confirmed 640 non-null vectors
  and 114 matches for `plainto_tsquery('english', 'wheel spoke')`. This is a
  candidate-count smoke check, not relevance evaluation or a latency benchmark.
- Six new tests verify cross-field AND/stemming, native weights and stable ties,
  omitted blank/canceled-only entries, missing descriptions, explicit rebuild
  after ingestion, repeatability, empty command JSON and actual GIN existence.
- Freshness boundary: new imports are not searchable until explicit rebuild;
  unchanged ingestion preserves vectors. Direct ORM/SQL edits can stale vectors.
  No automated freshness detector or concurrent ingestion/rebuild guarantee.
- PostgreSQL full-text position/size limits remain a baseline limitation,
  particularly for long descriptions; no claim of measured relevance quality.
- Next: validated search inputs, literal filters before pagination, counts/rank,
  traceable excerpts, then Ninja HTTP. No frontend or Part 3 selection added.
