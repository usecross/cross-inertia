

0.5.0 - 2025-11-25
------------------

Add `optional()` and `always()` prop types following Laravel Inertia conventions.

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
