# Frontend — Patent search workspace

Vite + React + TypeScript, selected for Part 3 **Interface at Scale**.
The visual foundation includes a navbar, editable search/filter fields,
illustrative patent cards and selectable empty/loading previews. Search is
disabled: there are no API calls, linked views or interaction measurements yet.

## Run locally

From the repository root, use `make frontend-install` once and
`make frontend-dev` to start Vite. `make frontend-check`, `make frontend-build`
and `make frontend-preview` wrap the corresponding npm scripts.
Build before preview; stop either frontend server with Ctrl+C.
These commands run on the host and do not change `make dev` or `make stop`,
which manage only the backend.

Use Node.js 22.12+ and npm (verified with Node 26.12.0 / npm 11.20.0).
From `frontend/`:

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to
`http://127.0.0.1:8000`, so local API requests need no extra CORS configuration.
The UI preview does not require Django. To use API routes, start the backend
with `make dev` from the repository root. This is a development proxy, not a
production deployment configuration.
If Django uses a different port, update the proxy target in `vite.config.ts`.

```sh
npm run check
npm run build
```

TypeScript and production build pass with the styling integration. Browser
rendering, linked-view interactions and accessibility have not been independently
tested.

## Styling and preview behavior

Tailwind CSS 4 uses the official `@tailwindcss/vite` plugin. daisyUI 5 is configured
in `src/styles.css` with `themes: corporate --default`; there is no custom theme
or JavaScript Tailwind configuration. Components use daisyUI classes and semantic
theme colors. React manages local input values, filter expansion and the state
preview selector; none of these controls performs a search.

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
