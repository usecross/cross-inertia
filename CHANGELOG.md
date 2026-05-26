0.19.1 - 2026-05-26
-------------------

Add automatic FastAPI validation error handling for Inertia requests.

- Store FastAPI and Pydantic validation errors in the session and expose them once as `page.props.errors`
- Use `_form` for Pydantic model-level validation errors
- Document the FastAPI validation error flow

This release was contributed by [@patrick91](https://github.com/patrick91) in [#132](https://github.com/usecross/cross-inertia/pull/132)

0.19.0 - 2026-05-26
-------------------

This release adds FastAPI validation error handling for Inertia form submissions.

- Add declarative FastAPI exception handlers for validation failures
- Store validation errors in the session and expose them once as `props.errors`
- Redirect validation failures back using the same-origin referrer or stored previous Inertia URL
- Preserve error bags for scoped form errors
- Update validation documentation to match the Inertia protocol

This release was contributed by [@patrick91](https://github.com/patrick91) in [#131](https://github.com/usecross/cross-inertia/pull/131)

0.18.0 - 2026-04-04
-------------------

Align Django adapter with FastAPI and Inertia v3 SSR model.

- Use Vite's `/__inertia_ssr` endpoint for SSR during development (both adapters)
- Move Vite/SSR server lifecycle from `AppConfig.ready()` to middleware
- Add configurable `asset_url_prefix` (Django derives from `STATIC_URL` by default)
- Add `SSR_CWD` setting for Django parity with FastAPI's `ssr_cwd`
- Deprecate `vite_tags` template variable in favour of `inertia_head()`/`inertia_body()`
- Return `Markup`/`mark_safe` from template helpers to prevent double-escaping

This release was contributed by [@patrick91](https://github.com/patrick91) in [#120](https://github.com/usecross/cross-inertia/pull/120)

0.17.0 - 2026-03-25
-------------------

Align with Inertia v3 stable protocol

- Add flash data support via `inertia.flash(key, value)`
- Add `preserveFragment` support via `inertia.preserve_fragment()`
- Add `X-Inertia-Redirect` for hash fragment redirects via `inertia.redirect(url)`
- Add `sharedProps` to page object (exposes shared prop keys for optimistic updates)
- Make `encryptHistory`/`clearHistory` optional in page object (only sent when `true`)
- Remove unused `_is_lazy_prop` backwards compat alias

This release was contributed by [@patrick91](https://github.com/patrick91) in [#119](https://github.com/usecross/cross-inertia/pull/119)

0.16.1 - 2026-03-24
-------------------

This release fixes a server-side rendering bug caused by reusing an async SSR HTTP client across closed event loops.

- Create a fresh `httpx.AsyncClient` for each SSR `render()` call
- Create a fresh `httpx.AsyncClient` for each SSR `health_check()` call
- Remove the cached async SSR client to avoid `Event loop is closed` errors on repeated requests
- Add tests covering repeated SSR renders and health checks across separate event loops
- Preserve graceful fallback to CSR when SSR fails

This release was contributed by [@patrick91](https://github.com/patrick91) in [#118](https://github.com/usecross/cross-inertia/pull/118)

0.16.0 - 2026-03-08
-------------------

Add shared v3 page building, once props, and script-element bootstrap support

- add the shared internal page builder used by both FastAPI and Django
- add public `once()` props with shared-data support, expiration, and refresh handling
- switch initial HTML page bootstrapping to Inertia's script-element format
- update the example app and docs site to the v3 client bootstrap flow
- add browser coverage for once props and refresh the existing E2E suite for the current demo UI
- update examples, docs, tests, and nox sessions for the new bootstrap flow

This release was contributed by [@patrick91](https://github.com/patrick91) in [#114](https://github.com/usecross/cross-inertia/pull/114)

0.15.0 - 2026-02-12
-------------------

This release adds the `@inertia_share` decorator for FastAPI, enabling
dependency-based shared data, and removes `InertiaMiddleware` for FastAPI.
Use FastAPI's `Depends()` naturally instead:

```python
from typing import Annotated
from fastapi import Depends, Request
from cross_inertia.fastapi import inertia_share

DB = Annotated[Session, Depends(get_db)]

@inertia_share
async def share_auth(request: Request, db: DB):
    return {"auth": {"user": get_user(db, request)}}

@inertia_share
async def share_flash(request: Request):
    return {"flash": request.session.get("flash", {})}

# request: Request is optional — auto-injected if missing
@inertia_share
async def share_counts(db: DB):
    return {"count": db.query(Cat).count()}

app = FastAPI(dependencies=[Depends(share_auth), Depends(share_flash), Depends(share_counts)])
```

Multiple `@inertia_share` functions compose by merging their return values.

**Breaking:** `InertiaMiddleware` has been removed for FastAPI. Replace
`app.add_middleware(InertiaMiddleware, share=fn)` with `@inertia_share` +
`Depends()`. The Django `InertiaMiddleware` is unchanged.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#99](https://github.com/usecross/cross-inertia/pull/99)

0.14.0 - 2026-02-03
-------------------

Make `vite_port="auto"` the default

- Change default `vite_port` from `5173` to `"auto"` so Vite automatically finds an available port
- Fix port detection to check both IPv4 and IPv6, preventing false positives when servers listen on IPv6
- All Vite-related classes and functions now read from config when port is not specified