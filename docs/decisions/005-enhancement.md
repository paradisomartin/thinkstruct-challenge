# D-005 — Part 3 enhancement

**Status:** Accepted direction · **Date:** 2026-11-16.

The user selected **Interface at Scale** as the primary Part 3 enhancement.
Implement linked results, hierarchical classification counts and a weekly
timeline, with shared filters, consistent counts and protection against stale
responses. Verify source date semantics before presenting a filing timeline.
Measure filter-to-render latency and document the dataset size and scale limits.
Adding a setup screen does not satisfy these criteria.

Use Vite + React + TypeScript inside `frontend/`, as explicitly approved.
React fits shared interactive state; Vite keeps the client setup small.
Astro/Starlight target content/documentation and add no needed capability here.
Django remains the API; the development Vite proxy avoids adding CORS for now.

Efficiency is a possible follow-up, not a second completed enhancement or an
authorization to download data. The formal large-data option requires the large
sample (or a portion), baseline measurements and measured improvements.
