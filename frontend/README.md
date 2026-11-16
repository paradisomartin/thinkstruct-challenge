# Frontend — Patent search workspace

Vite + React + TypeScript, selected for Part 3 **Interface at Scale**.
Only the workspace and setup screen are implemented; linked search views,
request-race protection and interaction measurements are still pending.

## Run locally

Use Node.js 22.12+ and npm (verified with Node 26.12.0 / npm 11.20.0).
Start the populated Django API with `make dev` from the repository root.
Then, from `frontend/`:

```sh
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to
`http://127.0.0.1:8000`, so local API requests need no extra CORS configuration.
This is a development proxy, not a production deployment configuration.
If Django uses a different port, update the proxy target in `vite.config.ts`.

```sh
npm run check
npm run build
```

`npm run preview` serves the built static app on port 4173, but does not provide
the development API proxy. Production hosting and API routing are not configured.
Dependencies are pinned and `package-lock.json` is committed. `node_modules/`
and `dist/` stay ignored. Browser-exposed variables must never contain backend
secrets. Django remains the sole backend; no Astro, Starlight or UI library.
