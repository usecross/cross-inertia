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
