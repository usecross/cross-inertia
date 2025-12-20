---
title: Middleware
description: API reference for InertiaMiddleware.
order: 13
section: API Reference
---

## InertiaMiddleware

The `InertiaMiddleware` handles Inertia-specific request/response processing.

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaMiddleware

app = FastAPI()
app.add_middleware(InertiaMiddleware, share=share_data)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `share` | `Callable[[Request], dict] \| None` | Function that returns shared props (optional) |

## Basic Usage (No Shared Data)

If you don't need to share data across all pages, you can add the middleware without a share function:

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaMiddleware

app = FastAPI()
app.add_middleware(InertiaMiddleware)  # No share function needed
```

When no share function is provided, no shared data is added to requests. You can still pass props directly to your Inertia responses.

## Share Function

The `share` parameter accepts a function that receives the request and returns a dictionary of props to share across all pages.

```python
from fastapi import Request

def share_data(request: Request) -> dict:
    return {
        "auth": {
            "user": get_current_user(request)
        },
        "flash": get_flash_messages(request),
        "app_name": "My App",
    }

app.add_middleware(InertiaMiddleware, share=share_data)
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
from inertia import always

def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even on partial reloads)
        "notifications_count": always(lambda: get_notifications_count()),
        # Only evaluated on full page loads
        "user": get_current_user(request),
    }
```
