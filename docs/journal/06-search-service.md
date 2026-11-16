# Search service and traceable evidence · 2026-11-16

- Implemented `patents.services.search.search_patents`: validated plain query,
  English stop-word rejection, classification prefix, literal title/abstract
  keywords and normalized whole-title equality. All constraints combine with AND.
- Count precedes pagination; native `ts_rank` descends with document-number ties.
  Filter-only requests sort by document number and have null scores.
- Literal filters use Python Unicode casefold/alphanumeric normalization over
  candidate metadata, selecting IDs before SQL count/rank/pagination. This is an
  explicit small-sample compromise, not a scalable metadata index. Classification
  and full-text constraints execute in PostgreSQL first.
- Evidence searches only page patents: matching claims before descriptions,
  then title/abstract. Any remaining query lexeme may explain a cross-field match;
  an excerpt does not promise every query term occurs in that passage.
  Return one complete, unmodified passage with original array index, or a scalar
  field with null index. No arbitrary truncation/highlight HTML. Classification-only
  lookup has null evidence; literal text-only lookup exposes its matching scalar.
- Tests cover ranking/ties, pagination/counts, combined constraints, Unicode,
  non-stemming/substrings, no-description fallback, provenance, invalid input,
  no matches, stop words and plain-text operator handling. Suite: **35 tests pass**.
- Real-data smoke: `wheel spoke` returned 114 patents; adding `B60B` returned 98.
  The first three filtered results had claim evidence. These observations are
  not relevance judgments or a timed comparison.
- Next: thin Ninja adapter, HTTP validation tests and Bruno assertions, then
  reproducible filtered/unfiltered latency measurements. Part 3 remains unselected.
