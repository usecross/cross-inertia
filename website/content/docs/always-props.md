---
title: Always Props
description: Props that are always included, even during partial reloads
---

Always props are props that are **always included** in Inertia responses, even when the client requests a partial reload with specific props. This is perfect for data that must always be fresh, like flash messages or notifications.

## The Problem

During [partial reloads](/guides/partial-reloads/), only the requested props are included in the response:

```python
@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "user": get_user(),
        "flash": get_flash_messages(),
        "stats": get_dashboard_stats(),
    })
```

```tsx
// Frontend: Only reload stats
router.reload({ only: ['stats'] })

// Result: Only 'stats' is returned
// Problem: 'flash' messages are missing!
```

## The Solution: Always Props

Wrap props with `always()` to ensure they're included in every response:

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "user": get_user(),
        "flash": always(get_flash_messages),  # Always included!
        "stats": get_dashboard_stats(),
    })
```

```tsx
// Frontend: Only reload stats
router.reload({ only: ['stats'] })

// Result: Both 'stats' AND 'flash' are returned
```

## Basic Usage

### With a Callable

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "notifications": always(get_notifications),
        "flash": always(get_flash_messages),
    })
```

### With Arguments

Pass arguments to the callable:

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    user = get_current_user()

    return inertia.render("Dashboard", {
        # Positional arguments
        "notifications": always(get_notifications, user.id),

        # Keyword arguments
        "alerts": always(get_alerts, user_id=user.id, limit=5),
    })
```

### With Static Values

You can also use `always()` with static values:

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "version": always("1.0.0"),
        "config": always({"theme": "dark"}),
    })
```

## Common Use Cases

### Flash Messages

Flash messages should always be delivered, even during partial reloads:

```python
from inertia import always

def get_flash(request: Request) -> dict | None:
    """Get and clear flash message from session."""
    if "flash" in request.session:
        return request.session.pop("flash")
    return None

@app.get("/users")
async def users_list(request: Request, inertia: InertiaDep):
    return inertia.render("Users/List", {
        "users": get_users(),
        "flash": always(get_flash, request),  # Always delivered
    })
```

### Notifications

User notifications should always be fresh:

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    user = get_current_user()

    return inertia.render("Dashboard", {
        "user": user,
        "stats": get_dashboard_stats(),
        "notifications": always(get_unread_notifications, user.id),
    })
```

```tsx
export default function Dashboard({ user, stats, notifications }) {
  const refreshStats = () => {
    // Refresh stats, but notifications are also updated
    router.reload({ only: ['stats'] })
  }

  return (
    <div>
      <NotificationBell count={notifications.length} />
      <button onClick={refreshStats}>Refresh Stats</button>
      <Stats data={stats} />
    </div>
  )
}
```

### CSRF Tokens

Security tokens should always be current:

```python
from inertia import always

@app.get("/settings")
async def settings(request: Request, inertia: InertiaDep):
    return inertia.render("Settings", {
        "user": get_current_user(),
        "csrf_token": always(lambda: request.state.csrf_token),
    })
```

### Real-Time Data

Data that must always reflect the latest state:

```python
from inertia import always

@app.get("/chat/{room_id}")
async def chat_room(room_id: int, inertia: InertiaDep):
    return inertia.render("Chat/Room", {
        "room": get_room(room_id),
        "messages": get_messages(room_id),
        "online_users": always(get_online_users, room_id),  # Always fresh
    })
```

## Cannot Be Excluded

Always props cannot be excluded using the `except` header:

```python
from inertia import always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "user": get_user(),
        "flash": always(get_flash),
        "stats": get_stats(),
    })
```

```tsx
// Frontend: Exclude flash
router.reload({ except: ['flash'] })

// Result: 'flash' is STILL included (always props cannot be excluded)
```

## Combining with Other Prop Types

Always props work alongside [optional](/guides/partial-reloads/) and [deferred](/guides/partial-reloads/) props:

```python
from inertia import always, optional, defer

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "user": get_user(),                          # Regular prop
        "flash": always(get_flash),                  # Always included
        "expensive_data": optional(get_expensive),   # Only when requested
        "analytics": defer(get_analytics),           # Loaded after render
    })
```

| Prop Type | Initial Load | Partial Reload (only) | Partial Reload (except) |
|-----------|--------------|----------------------|------------------------|
| Regular   | Included     | Only if requested    | Excluded if specified  |
| `always`  | Included     | **Always included**  | **Cannot be excluded** |
| `optional`| Excluded     | Only if requested    | Excluded if specified  |
| `defer`   | Excluded     | Only if requested    | Excluded if specified  |

## Best Practices

1. **Use sparingly**: Only use `always()` for props that truly need to be in every response
2. **Keep it lightweight**: Always props run on every request, so keep them fast
3. **Perfect for**: Flash messages, notifications, CSRF tokens, online status
4. **Avoid for**: Large datasets, expensive queries, static data

## API Reference

```python
from inertia import always

# With callable
always(callable)

# With callable and positional arguments
always(callable, arg1, arg2)

# With callable and keyword arguments
always(callable, key1=value1, key2=value2)

# With static value
always(static_value)
```

## Next Steps

- [Partial Reloads](/guides/partial-reloads/) - Learn about partial reload mechanics
- [Shared Data](/guides/shared-data/) - Share data across all pages
- [Configuration](/guides/configuration/) - Configure Cross-Inertia
