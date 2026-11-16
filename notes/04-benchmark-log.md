# 04 — Benchmarks & Validation

## Method

Document hardware, dataset size, query samples, warm/cold cache conditions, timing boundaries, and repetitions before reporting numbers.

## Search latency

| Test ID | Dataset size | Query | Filters | Runs | p50 (ms) | p95 (ms) | Notes |
|---|---:|---|---|---:|---:|---:|---|
| B-001 | TBD | TBD | None | TBD | TBD | TBD | Baseline |
| B-002 | TBD | Same as B-001 | Classification/title/abstract | TBD | TBD | TBD | Hybrid comparison |

## Correctness cases
- [ ] Keyword query returns relevant patent evidence
- [ ] Classification prefix (e.g., `B60B`) constrains results
- [ ] Title/abstract keyword filter constrains results
- [ ] Specific title lookup works
- [ ] Missing fields handled according to D-002
- [ ] Empty/no-match inputs behave sensibly
- [ ] Filtering and ranking remain deterministic

## If Interface at Scale is selected
- [ ] Three linked views reflect the same result set
- [ ] Filters are visible/removable in any order
- [ ] A new query preserves active filters
- [ ] Stale response results never override a newer query/filter state
- [ ] Time from filter change to consistent rendered views is measured
- [ ] README discusses implications at ~10 million patents
