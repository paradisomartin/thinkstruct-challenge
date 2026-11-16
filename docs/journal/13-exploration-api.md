# Versioned exploration API · 2026-11-16

- User approved a central `backend/api/v1/patents/` HTTP layer, API tests under
  `api/tests/`, separate patent/passage model files and domain tests under
  `patents/tests/`. Model exports preserve domain imports; migrations are unchanged.
- Moved search to `/api/v1/patents/search` and added `/api/v1/patents/explore`.
  Health/docs/OpenAPI remain at their existing paths. Updated Docker image
  contents, Make's test discovery, Bruno and current reproduction commands.
- Exploration reuses search validation/ranking/evidence and adds browse,
  inclusive source-date filters, hierarchical classification counts and a
  source-week distribution over the full filtered set.
- Source dates are derived from weekly JSON filenames, not asserted legal filing
  dates. Missing/invalid dates and classification groups have explicit counts.
- One read-only repeatable-read transaction keeps response views coherent.
  A regression updates metadata through a second database connection between
  aggregation and result rendering, verifying that the original snapshot survives.
- Verified **71 tests**, Django checks and no migration drift. Live Bruno:
  **9 requests / 10 script tests passed**. Live browse: **640 patents / 64 source
  weeks**, no unknown dates/classifications; one source date selects 10 patents.
  `wheel spoke`: 114; classification `B60B` plus title token `wheel`: 55.
- No reingestion or persistent data changes. Existing benchmark snapshots were
  not overwritten or rerun. These checks do not measure interface performance.
- Frontend remains a visual preview. Next: connect the three views to exploration,
  apply responses atomically, reject stale requests and measure filter updates.
