# Figma desktop adaptation · 2026-11-16

- User supplied desktop frame `3:2` and filters/states frame `3:4`, then updated
  the desktop background to a horizontal gradient from `#2B9CFF` to `#004E93`.
- Adapted the reference to existing React/daisyUI components rather than copying
  absolute-positioned generated markup. Corporate palette/radii are overridden;
  Mozilla Text is self-hosted through the already installed package.
- Compact search row, flat white cards, selected classification/keyword styling,
  source-week bars, evidence panels and loading/empty/error states follow the
  reference. Existing advanced filters remain even when absent from the mockup.
- Numbered pagination derives from the API total; Clear filters in the empty
  state preserves the query. Original abstracts/evidence remain unmodified.
- Vitest and live browser regressions pass in the Docker frontend; TypeScript and
  production build pass. Desktop screenshot compared against the Figma reference.
  Basic responsive classes remain, but user explicitly deprioritized mobile work.
- No static image assets were provided/needed. No API, schema or data changes.
  Historical production timing baseline remains unchanged; the latest browser
  run uses development mode and is not a new production performance claim.
- The supplied gradient has lower contrast under small white text at the light
  edge; matching it does not imply WCAG contrast certification.
- Pre-delivery verification: 71 backend tests, 4 Vitest tests, all 5 browser
  regression groups and Bruno's 9 requests / 10 tests pass. Django checks report
  no issues or migration drift; TypeScript, production build and local links pass.
