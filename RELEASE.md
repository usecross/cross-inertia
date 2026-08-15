---
release type: minor
---

Unify the Django adapter with `InertiaConfig`: its shared `CROSS_INERTIA`
settings now use the same defaults. In practice `VITE_PORT` defaults to
`"auto"` (a free port, as FastAPI always did) instead of `5173`, and
`VITE_ENTRY` defaults to `frontend/app.tsx` instead of `src/main.tsx` — set
them explicitly if you relied on the old Django defaults.

The Vite subprocess now receives `INERTIA_VITE_URL`, so `vite.config` can set
`server.origin` from it and no longer needs a hard-coded port. The health check
and log messages use the configured `vite_host` instead of `localhost`.
