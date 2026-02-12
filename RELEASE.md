---
release type: minor
---

This release adds the `@inertia_share` decorator for FastAPI, enabling
dependency-based shared data. Instead of manually constructing resources in
middleware, you can now use FastAPI's `Depends()` naturally:

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
app.add_middleware(InertiaMiddleware)  # no share= needed
```

Multiple `@inertia_share` functions compose by merging their return values.
Works alongside the existing `InertiaMiddleware(share=...)` pattern.
