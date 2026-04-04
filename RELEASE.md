---
release type: minor
---

Align Django adapter with FastAPI and Inertia v3 SSR model.

- Use Vite's `/__inertia_ssr` endpoint for SSR during development (both adapters)
- Move Vite/SSR server lifecycle from `AppConfig.ready()` to middleware
- Add configurable `asset_url_prefix` (Django derives from `STATIC_URL` by default)
- Add `SSR_CWD` setting for Django parity with FastAPI's `ssr_cwd`
- Deprecate `vite_tags` template variable in favour of `inertia_head()`/`inertia_body()`
- Return `Markup`/`mark_safe` from template helpers to prevent double-escaping
