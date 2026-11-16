# Search HTTP contract and repeatable API checks · 2026-11-16

- Split prior work into independently testable commits: `1c5de42` contains index
  rebuilding (25 tests verified from an export of the staged files), `2542c50`
  contains retrieval/filter/evidence service (35 tests).
- Added a thin patent-domain Ninja router, typed request/result/error schemas and
  `GET /api/patents/search`. Keyword lists use repeated query parameters.
  Domain and transport validation return 422; database failures return sanitized
  503 without logging query text or raw exception details.
- Verified **42 tests pass**: HTTP serialization/provenance, repeated terms,
  combined filters, title lookup/pagination, invalid parameters, no matches,
  sanitized database failure and generated OpenAPI. Django checks pass and
  migration drift check reports no changes.
- A ranking test initially assumed an extra matching claim must improve native
  multi-term `ts_rank`. That assumption failed; kept the accepted ranking method
  and isolated provenance via a classification filter rather than fabricating
  a desired order.
- `make dev` started healthy and `make openapi` exported the updated live schema.
  `make api-test`: **8 requests, 9 script tests pass** against the supplied dataset.
  Includes expected 422 responses; no database-failure injection in the live API.
- Bruno initially ignored scripts outside `runtime.scripts`; corrected their
  placement and confirmed nonzero executed tests. Script tests contain assertions;
  Bruno's separate declarative Assertions counter remains zero.
- Collection tests reuse baseline search runtime variables in sequence and require
  ingestion plus explicit rebuilding. Reports remain ignored with bodies/headers
  omitted. Individual HTTP durations are diagnostics, not a controlled benchmark.
- Next slice: reproducible filtered/unfiltered measurements with disclosed dataset,
  hardware, warmup/repetitions, timing boundary and aggregation. Part 2 PoC and
  Part 3 enhancement remain unselected.
