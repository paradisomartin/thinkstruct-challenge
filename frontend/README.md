# Frontend — Patent search workspace

Vite + React + TypeScript, selected for Part 3 **Interface at Scale**.
Three live views share `/api/v1/patents/explore`: results with original-text
evidence, classification drill-down and a selectable source-week distribution.
Active filters are individually removable; submitting a new query preserves
the other filters. Keywords are space-separated AND terms.

## Run locally

From the repository root, use `make frontend-install` once and
`make frontend-dev` to start Vite. `make frontend-check`, `make frontend-build`
and `make frontend-preview` wrap the corresponding npm scripts.
Build before preview; stop either frontend server with Ctrl+C.
These npm commands run on the host. `make dev` starts the backend;
`make stop` stops Compose services, not a host-run Vite process.

Use Node.js 22.12+ and npm (verified with Node 26.12.0 / npm 11.20.0).
From `frontend/`:

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to
`http://127.0.0.1:8000`, so local API requests need no extra CORS configuration.
Start Django with `make dev` from the repository root, ingest the supplied sample
and rebuild its index as described in the root README. This is a development proxy, not a
production deployment configuration.
If Django uses a different host port, set
`API_PROXY_TARGET=http://127.0.0.1:8001 make frontend-dev`.
The proxy target is server-side configuration, not a browser-exposed secret.

```sh
npm run check
npm run build
```

## Optional Docker development

After root `.env` setup, from the repository root:

```sh
make dev-all
make frontend-docker-test
```

No host Node installation is needed. Open `http://127.0.0.1:5173`.
If local Vite is already running, stop it with Ctrl+C, or run
`make dev-all FRONTEND_PORT=5174` to use `http://127.0.0.1:5174`.
Data ingestion/indexing follow the root README and are not done automatically.

Compose profile `frontend` is opt-in; ordinary `make dev` remains backend-only.
The digest-pinned Node 26 image runs as the non-root `node` user, binds Vite
inside the container to `0.0.0.0`, and publishes only to host loopback.
`API_PROXY_TARGET=http://app:8000` routes browser `/api` requests to Django
through Compose DNS, regardless of the API's published host port.

Source is bind-mounted for reload. `frontend_node_modules` is a separate named
volume, so Linux dependencies never replace host `node_modules`. Startup runs
`npm ci` before Vite to refresh dependencies after lockfile changes; this needs
npm registry access and adds startup time. Do not install host dependencies while
host Vite is running. Container dependency refreshes are isolated from it.

`make frontend-docker-stop` stops just this service; `make stop` also stops it
alongside the API/database without deleting volumes. To return to local mode,
stop the Docker frontend, then run `make frontend-dev`.
This is a development setup, not production static hosting or a change to Part 2's PoC.

## Verification and measurements

Fast integration tests (no Django, browser binary or running servers required):

```sh
make frontend-unit-test
# Or from frontend/: npm test
# Watch mode: npm run test:watch
```

Four Vitest + Testing Library tests render the full app in jsdom with mocked
HTTP responses: linked classification/week filters, query/filter preservation
and removal, empty/error/retry, and stale successes/errors despite ignored abort.
Fixtures are synthetic. These are frontend integration tests, not full-stack E2E;
the real-browser suite below verifies the live API and measures render updates.

Use the supplied 640-patent sample and production bundle. From the repository root:

```sh
make frontend-build
make frontend-preview
# In another terminal, API and preview running:
make frontend-test
```

The runner needs Python 3 and `agent-browser` (verified: 0.39.1).
If absent, install with `npm install -g agent-browser`, then
`agent-browser install` for browser binaries. This is a local tool, not an app dependency.
`make frontend-test URL=http://127.0.0.1:5173` tests development mode;
do not compare those timings directly with the production baseline.
For Docker development, use `make frontend-test URL=http://127.0.0.1:5173`
(or the selected `FRONTEND_PORT`). The browser runner still runs on the host.

The runner creates/closes its own browser session and writes ignored
`artifacts/frontend-exploration.json`. It checks linked counts, paging, drill-down,
dates, filter preservation/removal, empty/error/retry and out-of-order responses
using controlled promises that ignore abort. It measures 20 warm classification
updates after 3 warmups. [Method/results](../docs/benchmarks/003-linked-interface.md).

`useExplore` aborts superseded requests and independently checks an increasing
request ID. Filter changes clear the entire old response; each new response
commits all views together. `performance` entries named `explore-update` measure
from the request handler through two animation frames after React commits.
This is a paint-opportunity approximation, not physical-display measurement.

## Styling

Tailwind CSS 4 uses the official `@tailwindcss/vite` plugin. daisyUI 5 retains
`corporate` as the base, with Figma-derived palette/radius overrides in
`src/styles.css`; no JavaScript Tailwind configuration or extra UI library.
Mozilla Text is self-hosted through the existing Fontsource package.

The [desktop Figma reference](https://www.figma.com/design/nhVo8ZpPfyB6G3dEk62ijB/Thinkstruct-Challenge---Martin-Paradiso?node-id=3-2)
supplies the horizontal sky-to-deep-blue gradient, flat white cards, compact
search bar, hierarchy, metadata badges and evidence/state surfaces. React keeps
all existing filters, including title/abstract fields omitted from the mockup.
Real abstracts remain complete instead of copying the mockup's truncated text.
Pagination numbers use the API's real total/offset; empty-state Clear filters
preserves the query. No Figma sample counts or patent text are hard-coded.
Desktop is the visual verification target; mobile keeps basic responsive layout,
without a separate mobile design pass.

References: [React installation](https://daisyui.com/docs/install/react/),
[themes](https://daisyui.com/docs/themes/),
[components](https://daisyui.com/components/) and
[Tailwind Vite integration](https://tailwindcss.com/docs/installation/using-vite).

After `npm run build`, `npm run preview` serves the built app on port 4173.
In the pinned Vite version, preview inherits the `/api` proxy from `server.proxy`;
requests through that proxy need Django on port 8000. This is a local preview server;
production hosting and API routing are not configured.
Dependencies are pinned with `package-lock.json`. `node_modules/`
and `dist/` stay ignored. Browser-exposed variables must never contain backend
secrets. Django remains the sole backend; no Astro, Starlight or additional UI library.
