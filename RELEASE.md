---
release type: minor
---

Improve Vite development-server support across Django and FastAPI.

- Honour `vite_base` / `VITE_BASE` in health checks, reachability probes, and
  injected development script tags, so non-root Vite base paths work.
- Include the resolved command, health URL, and recent Vite output in startup
  errors.
- Align Django's shared defaults with `InertiaConfig`, including an automatic
  Vite port and the `frontend/app.tsx` entry point.
- Export the resolved `INERTIA_VITE_URL` to Vite so `server.origin` does not
  need a hard-coded port, and use the configured `vite_host` consistently.
