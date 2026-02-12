---
title: Shared Data
description: Share data across all pages using the @inertia_share decorator.
order: 5
section: Core Concepts
---

## What is shared data?

Shared data is data that is automatically included in every Inertia response. This is useful for data that is needed on every page, such as:

- Current user information
- Flash messages
- Navigation data
- Application settings

## Setting up shared data

### FastAPI

Use the `@inertia_share` decorator to define shared data providers as FastAPI dependencies:

```python
from fastapi import Depends, FastAPI, Request
from cross_inertia.fastapi import inertia_share

@inertia_share
def share_data(request: Request) -> dict:
    return {
        "auth": {
            "user": get_current_user(request)
        },
        "flash": get_flash_messages(request),
        "app_name": "My App"
    }

app = FastAPI(dependencies=[Depends(share_data)])
```

You can split shared data into multiple functions:

```python
@inertia_share
async def share_auth(request: Request) -> dict:
    return {"auth": {"user": get_current_user(request)}}

@inertia_share
async def share_flash(request: Request) -> dict:
    return {"flash": get_flash_messages(request)}

app = FastAPI(dependencies=[Depends(share_auth), Depends(share_flash)])
```

The `request: Request` parameter is optional — if omitted, it is auto-injected:

```python
@inertia_share
async def share_counts(db: DB) -> dict:
    return {"count": db.query(Cat).count()}
```

### Django

Define a share function and reference it in your settings:

```python
# myapp/inertia.py
def share_data(request):
    return {
        "auth": {
            "user": request.user.username if request.user.is_authenticated else None
        },
        "flash": request.session.pop("flash", None),
        "app_name": "My App"
    }
```

```python
# settings.py
CROSS_INERTIA = {
    "SHARE": "myapp.inertia.share_data",
}
```

## Accessing shared data

Shared data is merged with page props. Access it using the `usePage` hook:

```tsx
import { usePage } from '@inertiajs/react'

interface SharedProps {
  auth: {
    user: { name: string } | null
  }
  flash: {
    message?: string
    type?: 'success' | 'error'
  }
}

export default function Layout({ children }) {
  const { auth, flash } = usePage<{ props: SharedProps }>().props

  return (
    <div>
      {auth.user && <span>Hello, {auth.user.name}</span>}
      {flash.message && (
        <div className={`alert alert-${flash.type}`}>
          {flash.message}
        </div>
      )}
      {children}
    </div>
  )
}
```

## Lazy shared data

You can use `always()` to ensure data is always evaluated, even during partial reloads:

```python
from cross_inertia import always

@inertia_share
def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even on partial reloads)
        "notifications_count": always(lambda: get_notifications_count()),
        # Only evaluated on full page loads
        "user": get_current_user(request)
    }
```
