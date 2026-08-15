---
release type: minor
---

Add `vite_base` / `VITE_BASE` so the Vite dev server can be served under a
non-root `base` (for example `/static/build/`, common when Django serves the
built assets from there). The dev-mode health check, the reachability probe and
the injected `@vite/client`, `@react-refresh` and entry script tags now honour
it; previously they always assumed `/`, so a non-root `base` made the health
check time out, the auto-started Vite process get killed and pages silently
fall back to the production manifest.

Vite startup failures now include the resolved command, the health-check URL
and the last lines of Vite's output, and Django's `runserver` prints the exact
command it is running — a command that rejects the appended `--port` (such as
`bun --cwd frontend run dev`) is now obvious instead of a silent fallback.

Unify the Django adapter with `configure_inertia()`: every shared
`CROSS_INERTIA` key now defaults to the `InertiaConfig` value. In practice
`VITE_PORT` defaults to `"auto"` (a free port, as FastAPI always did) instead
of `5173`, and `VITE_ENTRY` defaults to `frontend/app.tsx` instead of
`src/main.tsx` — set them explicitly if you relied on the old Django defaults.

The Vite subprocess now receives `INERTIA_VITE_URL`, `INERTIA_VITE_PORT` and
`INERTIA_VITE_BASE`, so `vite.config` can set `server.origin` from
`process.env.INERTIA_VITE_URL` and no longer needs a hard-coded port. The
health check and log messages use the configured `vite_host` instead of
`localhost`.
