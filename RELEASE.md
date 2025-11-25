---
release type: minor
---

Add `optional()`, `always()`, and `defer()` prop types following Laravel Inertia conventions.

## New Features

### Callable Props (auto-invoke)
Automatically invoke callable props (lambdas, functions) during render:

```python
return inertia.render("Page", {
    "user": lambda: get_user(),  # Invoked automatically
    "data": get_user_async,      # Async callables are awaited
})
```

### Optional Props
Props that are excluded on initial load and only included when explicitly requested via partial reload:

```python
from inertia import optional

return inertia.render("Page", {
    "user": get_user(),                           # Always included
    "permissions": optional(get_permissions),     # Only when requested
    "activity": optional(get_activity, limit=10), # Supports args like functools.partial
})
```

Frontend usage:
```javascript
router.reload({ only: ["permissions"] })
```

### Always Props
Props that are always included, even during partial reloads:

```python
from inertia import always

return inertia.render("Page", {
    "user": get_user(),
    "flash": always(get_flash_messages),  # Always included
    "csrf": always(get_csrf_token),       # Even in partial reloads
})
```

### Deferred Props
Props that are excluded from the initial page load and automatically fetched by the Inertia client after the page renders:

```python
from inertia import defer

return inertia.render("Dashboard", {
    "user": get_user(),                    # Loaded immediately
    "analytics": defer(get_analytics),     # Loaded after page renders
})
```

#### Grouping for Parallel Loading
Props in the same group load together; different groups load in parallel:

```python
{
    "analytics": defer(get_analytics),                        # default group
    "notifications": defer(get_notifications),                # default group (loads with analytics)
    "recommendations": defer(get_recommendations, group="sidebar"),  # loads in parallel
}
```

#### Arguments Support
Like `functools.partial`, you can pass arguments to the callback:

```python
defer(get_user_stats, user_id, include_history=True)
