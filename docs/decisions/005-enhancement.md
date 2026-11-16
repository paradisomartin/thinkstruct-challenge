# D-005 — Part 3 enhancement

**Status:** Accepted direction · **Date:** 2026-11-16.

The user selected **Interface at Scale** as the primary Part 3 enhancement.
Implement linked results, hierarchical classification counts and a weekly
timeline, with shared filters, consistent counts and protection against stale
responses. Verify source date semantics before presenting a filing timeline.
Measure filter-to-render latency and document the dataset size and scale limits.
The visual preview and API data contract do not yet satisfy the linked-view criteria.

Use Vite + React + TypeScript inside `frontend/`, as explicitly approved.
React fits shared interactive state; Vite keeps the client setup small.
Astro/Starlight target content/documentation and add no needed capability here.
Django remains the API; the development Vite proxy avoids adding CORS for now.

The approved styling foundation uses Tailwind CSS 4's official Vite plugin and
daisyUI 5's built-in `corporate` theme through CSS configuration. React owns
behavior; daisyUI supplies styles, not search logic. The current UI is a visual
preview with illustrative cards, not a completed linked-view enhancement.

## Accepted exploration contract

`GET /api/v1/patents/explore` adds browse and linked-view data while reusing the
search service's text/filter/ranking/evidence rules. Unlike `/search`, an empty
request browses all patents, ordered by document number.

- `source_week_from` / `source_week_to`: inclusive dates, combined with the other
  filters by AND. Equal bounds select one batch date. Reversed ranges return 422.
- **Source week** means the date on `patents_ipaYYMMDD.json` (20YY). It is a weekly
  source-batch label, not a verified legal filing date or an ISO Monday week.
  Nested source paths are supported. Unrecognized/invalid dates remain null;
  XML filenames are not used as a fallback. Date filters exclude unknown dates.
- Results add nullable `source_week`. The response retains `total_matches` and
  normalized `effective_request`.
- `classification_facets` groups three-character prefixes (e.g. `B60`) with
  four-character children (`B60B`). Children partition their parent. The original
  classification string is preserved in results; unknown/unrecognized codes
  contribute to `unclassified_count` instead of being silently dropped.
- `source_weeks` is a date-ordered list of `{source_week, count}`;
  `unknown_source_week_count` covers missing/unrecognized dates.
- All counts cover the **entire filtered set before pagination**, including the
  selected classification and dates. These are not disjunctive facets. Parent
  counts plus unclassified count, and dated counts plus unknown-date count,
  each equal `total_matches`; paging changes only results.

One read-only PostgreSQL `REPEATABLE READ` transaction covers eligibility,
aggregation, ranking and evidence. This keeps one response internally coherent
under concurrent writes; it does not freeze subsequent requests. The frontend
must still reject stale responses and apply each response's views together.
Classification/date aggregation currently scans compact candidate metadata in
Python. It needs persisted/indexed dates and database aggregation at larger scale.

Efficiency is a possible follow-up, not a second completed enhancement or an
authorization to download data. The formal large-data option requires the large
sample (or a portion), baseline measurements and measured improvements.
