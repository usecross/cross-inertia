---
title: Shared Data
description: Share data across all Inertia pages
---

Shared data is automatically included in every Inertia response, making it perfect for authentication state, flash messages, and other global data that every page needs.

## What is Shared Data?

Shared data is props that are automatically included on every Inertia page without having to manually pass them in each route handler. Common use cases:

- Current authenticated user
- Flash messages (success, error, info)
- CSRF tokens
- App-wide settings
- Notification counts
- Shopping cart totals

## Basic Setup

Configure shared data when adding the Inertia middleware:

```python
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from inertia.fastapi import InertiaMiddleware

app = FastAPI()

def share_data(request: Request) -> dict:
    """
    This function is called for every Inertia request.
    Return data that should be shared across all pages.
    """
    return {
        "app_name": "My Application",
        "version": "1.0.0",
    }

# Add middleware (order matters!)
app.add_middleware(InertiaMiddleware, share=share_data)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

## Authentication Example

```python
from fastapi import Request
from inertia.fastapi import InertiaMiddleware

def share_data(request: Request) -> dict:
    """Share authentication state across all pages"""
    
    # Get authenticated user from session
    user = None
    if "user_id" in request.session:
        user = get_user_by_id(request.session["user_id"])
    
    return {
        "auth": {
            "user": user.to_dict() if user else None,
            "is_authenticated": user is not None,
        }
    }

app.add_middleware(InertiaMiddleware, share=share_data)
```

Access in any component:

```tsx
import { usePage } from '@inertiajs/react'

export default function Navigation() {
  const { auth } = usePage().props

  return (
    <nav>
      {auth.is_authenticated ? (
        <div>
          <span>Welcome, {auth.user.name}!</span>
          <a href="/logout">Logout</a>
        </div>
      ) : (
        <a href="/login">Login</a>
      )}
    </nav>
  )
}
```

## Flash Messages

Flash messages are one-time notifications that appear after actions (like form submissions):

```python
from fastapi import Request
from inertia.fastapi import InertiaMiddleware

def share_data(request: Request) -> dict:
    """Share flash messages across all pages"""
    flash_data = {}
    
    try:
        if "session" in request.scope and "flash" in request.session:
            # Only pop flash on GET requests (after redirects)
            if request.method == "GET":
                flash_data = request.session.pop("flash", {})
    except (KeyError, AssertionError):
        # Session not available
        pass
    
    return {
        "flash": flash_data,
    }

app.add_middleware(InertiaMiddleware, share=share_data)

# Helper function for setting flash messages
def flash(request: Request, message: str, category: str = "success"):
    """Flash a message to be displayed on the next request"""
    request.session["flash"] = {
        "message": message,
        "category": category,  # success, error, warning, info
    }
```

Using flash messages in routes:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from inertia.fastapi import InertiaDep

@app.post("/users")
async def create_user(inertia: InertiaDep):
    form_data = await inertia.request.json()
    
    # Validate and create user
    user = create_user(form_data)
    
    # Set flash message
    flash(inertia.request, "User created successfully!", "success")
    
    # Redirect (flash will be shown after redirect)
    return RedirectResponse(url=f"/users/{user.id}", status_code=303)

@app.post("/users/{user_id}/delete")
async def delete_user(user_id: int, inertia: InertiaDep):
    delete_user(user_id)
    
    flash(inertia.request, "User deleted", "info")
    return RedirectResponse(url="/users", status_code=303)
```

Display flash messages in your layout:

```tsx
import { usePage } from '@inertiajs/react'
import { useEffect, useState } from 'react'

export default function Layout({ children }) {
  const { flash } = usePage().props
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (flash?.message) {
      setVisible(true)
      // Auto-hide after 5 seconds
      const timer = setTimeout(() => setVisible(false), 5000)
      return () => clearTimeout(timer)
    }
  }, [flash])

  return (
    <div>
      {visible && flash?.message && (
        <div className={`alert alert-${flash.category}`}>
          {flash.message}
          <button onClick={() => setVisible(false)}>×</button>
        </div>
      )}
      
      <main>{children}</main>
    </div>
  )
}
```

## Complete Real-World Example

Here's a full example with authentication, flash messages, and counters:

```python
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from inertia.fastapi import InertiaMiddleware, InertiaDep

app = FastAPI()

def share_data(request: Request) -> dict:
    """Share data across all Inertia pages"""
    
    # Get authenticated user
    user_data = None
    if "user_id" in request.session:
        user = get_user_by_id(request.session["user_id"])
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar_url,
        }
    
    # Get dynamic counters
    favorites_count = 0
    notifications_count = 0
    cart_total = 0
    
    if user_data:
        favorites_count = count_user_favorites(user_data["id"])
        notifications_count = count_unread_notifications(user_data["id"])
        cart_total = get_cart_total(user_data["id"])
    
    # Get flash messages (only on GET requests)
    flash_data = {}
    try:
        if "flash" in request.session and request.method == "GET":
            flash_data = request.session.pop("flash")
    except (KeyError, AssertionError):
        pass
    
    return {
        "auth": {
            "user": user_data,
        },
        "favorites_count": favorites_count,
        "notifications_count": notifications_count,
        "cart_total": cart_total,
        "flash": flash_data,
    }

# Add middleware
app.add_middleware(InertiaMiddleware, share=share_data)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Helper for flash messages
def flash(request: Request, message: str, category: str = "success"):
    request.session["flash"] = {"message": message, "category": category}

# Routes
@app.post("/favorites/{item_id}/toggle")
async def toggle_favorite(item_id: int, inertia: InertiaDep):
    is_favorited = toggle_favorite_item(item_id)
    
    if is_favorited:
        flash(inertia.request, "Added to favorites!", "success")
    else:
        flash(inertia.request, "Removed from favorites", "info")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/items/{item_id}", status_code=303)
```

Frontend components:

```tsx
// Navigation.tsx
import { usePage } from '@inertiajs/react'

export default function Navigation() {
  const { auth, favorites_count, notifications_count, cart_total } = usePage().props

  return (
    <nav>
      {auth.user ? (
        <div className="user-menu">
          <img src={auth.user.avatar} alt={auth.user.name} />
          <span>{auth.user.name}</span>
          
          <a href="/favorites">
            Favorites
            {favorites_count > 0 && <span className="badge">{favorites_count}</span>}
          </a>
          
          <a href="/notifications">
            Notifications
            {notifications_count > 0 && <span className="badge">{notifications_count}</span>}
          </a>
          
          <a href="/cart">
            Cart
            {cart_total > 0 && <span className="total">${cart_total}</span>}
          </a>
          
          <a href="/logout">Logout</a>
        </div>
      ) : (
        <a href="/login">Login</a>
      )}
    </nav>
  )
}
```

## Optimizing Shared Data with Partial Reloads

Shared data is included in every response, even partial reloads. For expensive operations, use lazy evaluation:

```python
def share_data(request: Request) -> dict:
    user_id = request.session.get("user_id")
    
    return {
        "auth": {
            "user": get_user(user_id) if user_id else None,
        },
        # Lazy: only executed when specifically requested
        "notifications": lambda: get_notifications(user_id) if user_id else [],
    }
```

Then request it when needed:

```tsx
import { router } from '@inertiajs/react'

// Reload notifications from shared data
router.reload({ only: ['notifications'] })
```

## Conditional Shared Data

Only share data when needed:

```python
def share_data(request: Request) -> dict:
    data = {}
    
    # Always share auth
    user = get_current_user(request)
    data["auth"] = {"user": user}
    
    # Only share admin data on admin routes
    if request.url.path.startswith("/admin"):
        data["admin"] = {
            "permissions": get_admin_permissions(user),
            "stats": get_admin_stats(),
        }
    
    # Only share cart on shop routes
    if request.url.path.startswith("/shop"):
        data["cart"] = get_cart(user.id) if user else None
    
    return data
```

## Type Safety (TypeScript)

Define shared props type for TypeScript:

```tsx
// types/inertia.ts
export interface SharedProps {
  auth: {
    user: User | null
  }
  favorites_count: number
  notifications_count: number
  flash?: {
    message: string
    category: 'success' | 'error' | 'warning' | 'info'
  }
}

// Use in components
import { usePage } from '@inertiajs/react'
import { SharedProps } from './types/inertia'

export default function MyComponent() {
  const { auth, flash } = usePage<SharedProps>().props
  
  return (
    <div>
      {auth.user && <p>Hello, {auth.user.name}</p>}
      {flash?.message && <div className={flash.category}>{flash.message}</div>}
    </div>
  )
}
```

## Best Practices

1. **Keep it Lightweight**: Don't query expensive data on every request
2. **Use Lazy Evaluation**: Wrap expensive queries in lambdas
3. **Conditional Loading**: Only load data needed for specific routes
4. **Cache When Possible**: Cache frequently accessed shared data
5. **Flash on Redirects**: Only pop flash messages on GET requests
6. **Type Everything**: Use TypeScript for type-safe shared props

## Common Pitfalls

### ❌ Don't: Query expensive data on every request

```python
# Bad: Slow query runs on every request
def share_data(request: Request) -> dict:
    return {
        "stats": calculate_expensive_stats(),  # Runs every time!
    }
```

```python
# Good: Use lazy evaluation or caching
def share_data(request: Request) -> dict:
    return {
        "stats": lambda: calculate_expensive_stats(),  # Only when requested
    }
```

### ❌ Don't: Pop flash on POST requests

```python
# Bad: Flash message lost before redirect
def share_data(request: Request) -> dict:
    return {
        "flash": request.session.pop("flash", {})  # Pops on every request!
    }
```

```python
# Good: Only pop on GET requests
def share_data(request: Request) -> dict:
    flash_data = {}
    if request.method == "GET" and "flash" in request.session:
        flash_data = request.session.pop("flash", {})
    return {"flash": flash_data}
```

### ❌ Don't: Share sensitive data unconditionally

```python
# Bad: Shares admin data with everyone
def share_data(request: Request) -> dict:
    return {
        "admin_secrets": get_admin_secrets(),  # Exposed to all users!
    }
```

```python
# Good: Conditionally share based on permissions
def share_data(request: Request) -> dict:
    user = get_current_user(request)
    data = {}
    
    if user and user.is_admin:
        data["admin_panel"] = get_admin_panel_data()
    
    return data
```

## Next Steps

- [Partial Reloads](/guides/partial-reloads/) - Optimize shared data loading
- [Validation Errors](/guides/validation-errors/) - Combine flash with validation
- [History Encryption](/guides/history-encryption/) - Secure shared data
