---
title: Shared Data (FastAPI)
description: API reference for @inertia_share decorator.
order: 13
section: API Reference
---

## @inertia_share

The `@inertia_share` decorator marks a function as an Inertia shared data provider. Use it with FastAPI's `Depends()` to share data across all pages.

```python
from fastapi import Depends, FastAPI, Request
from cross_inertia.fastapi import inertia_share

@inertia_share
def share_data(request: Request) -> dict:
    return {
        "auth": {"user": get_current_user(request)},
        "flash": get_flash_messages(request),
        "app_name": "My App",
    }

app = FastAPI(dependencies=[Depends(share_data)])
```

## How it works

The decorator wraps your function so that its return value is merged into `request.state.inertia_shared`. This data is then automatically included in every Inertia response.

## Multiple share functions

You can compose multiple share functions. Their return values are merged:

```python
@inertia_share
async def share_auth(request: Request) -> dict:
    return {"auth": {"user": get_current_user(request)}}

@inertia_share
async def share_flash(request: Request) -> dict:
    return {"flash": get_flash_messages(request)}

app = FastAPI(dependencies=[Depends(share_auth), Depends(share_flash)])
```

## Auto-injection of request

If your function doesn't declare a `request: Request` parameter, one is automatically injected so FastAPI's dependency injection still works:

```python
@inertia_share
async def share_counts(db: DB) -> dict:
    # request is auto-injected behind the scenes
    return {"count": db.query(Cat).count()}
```

## Route-level dependencies

You can also use `@inertia_share` at the route level instead of globally:

```python
@app.get("/dashboard", dependencies=[Depends(share_dashboard_stats)])
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {})
```

## Accessing Shared Data

Shared data is merged with page props. Access it using the `usePage` hook:

```tsx
import { usePage } from '@inertiajs/react'

export default function Layout({ children }) {
  const { auth, flash } = usePage().props

  return (
    <div>
      {auth.user && <span>Hello, {auth.user.name}</span>}
      {children}
    </div>
  )
}
```

## Lazy Evaluation

Use `always()` to ensure data is always evaluated, even during partial reloads:

```python
from cross_inertia import always

@inertia_share
def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even on partial reloads)
        "notifications_count": always(lambda: get_notifications_count()),
        # Only evaluated on full page loads
        "user": get_current_user(request),
    }
```
