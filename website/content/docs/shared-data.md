---
title: Shared Data
description: Share data across all pages using middleware.
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

Use the `InertiaMiddleware` to define shared data:

```python
from fastapi import FastAPI, Request
from inertia.fastapi import InertiaMiddleware

app = FastAPI()

def share_data(request: Request) -> dict:
    return {
        "auth": {
            "user": get_current_user(request)
        },
        "flash": get_flash_messages(request),
        "app_name": "My App"
    }

app.add_middleware(InertiaMiddleware, share=share_data)
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
from inertia import always

def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even on partial reloads)
        "notifications_count": always(lambda: get_notifications_count()),
        # Only evaluated on full page loads
        "user": get_current_user(request)
    }
```
