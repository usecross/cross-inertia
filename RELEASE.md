---
release type: minor
---

This release adds the `@inertia_share` decorator for FastAPI, enabling
dependency-based shared data. Instead of manually constructing resources in
middleware, you can now use FastAPI's `Depends()` naturally:

```python
from cross_inertia.fastapi import inertia_share

@inertia_share
async def share_auth(request: Request, db: Session = Depends(get_db)):
    return {"auth": {"user": get_user(db, request)}}

@inertia_share
async def share_flash(request: Request):
    return {"flash": request.session.get("flash", {})}

# request: Request is optional — auto-injected if missing
@inertia_share
async def share_counts(db: Session = Depends(get_db)):
    return {"count": db.query(Cat).count()}

app = FastAPI(dependencies=[Depends(share_auth), Depends(share_flash), Depends(share_counts)])
app.add_middleware(InertiaMiddleware)  # no share= needed
```

Multiple `@inertia_share` functions compose by merging their return values.
Works alongside the existing `InertiaMiddleware(share=...)` pattern.
