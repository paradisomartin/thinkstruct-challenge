# Ranking regression and independent checks · 2026-11-16

- Part 1 review found that Django wraps string arguments to `SearchRank` in
  `SearchVector`: the service ranked `to_tsvector(search_vector::text)` instead
  of the weighted stored vector. Passage ranking had the same issue.
- Confirmed via generated SQL and read-only SQL values: direct single-term rank
  was 0.6079271 for A versus 0.06079271 for D; the old expression returned
  0.06079271 for both. Earlier test IDs masked equal-score ordering.
- Added regressions first and ran them before the fix: score, weight and excerpt
  assertions failed. Fixed both expressions with `F(...)`, including the original
  test helper; no reimport or index rebuild was required by this correction.
- Added coverage for SQL-reference scores, inverted-ID weights, term-frequency
  evidence, passage ties/claim preference, stable real-tie pagination, claim-only
  and description-only patents, empty-lexeme punctuation, repeated terms,
  apostrophes, hyphens/operators and database default-language independence.
- Verified **55 tests pass**, Django checks/migration consistency, and **8 Bruno
  requests / 9 script tests pass**. The new tests caught what the previous suite
  missed; passing tests alone were not sufficient evidence of correct weighting.
- Re-ran the same benchmark protocol. Preserved 001 as historical with a defect
  warning, and published [002](../benchmarks/002-search-ranking-fix.md) with its
  full JSON snapshot. Filter latency effects are mixed, not uniformly beneficial.
