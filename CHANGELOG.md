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