# Reproducible search baseline · 2026-11-16

- Added `benchmark_search` management command and `make benchmark`. The command
  checks nonempty/complete indexing and response stability, alternates variant
  order, and reports raw samples with p50/p95. It does not modify patents.
- Verified **46 tests pass**, including aggregation, incomplete-index rejection,
  command output and unstable-response rejection. Django/migration checks pass.
- Ran four query/filter pairs against the 640-patent database. Environment,
  methodology, actual results and caveats live in the
  [baseline report](../benchmarks/001-search-baseline.md), not duplicated here.
- Preserved the selected report's full JSON values under `docs/benchmarks/results/`;
  future executions write only to ignored `artifacts/`. No patent text or secrets.
- Accepted indexed benchmark documentation: one report per selected experiment,
  immutable numbered snapshots, short root README and checkpoint entries.
- Part 1 now has a tested search API and local timed filtered/unfiltered comparison.
  Part 2 costs/design/designated PoC, one Part 3 enhancement and final delivery
  verification/video remain pending. No at-scale performance claim.
