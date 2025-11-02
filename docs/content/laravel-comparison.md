# Laravel vs FastAPI Inertia - Feature Comparison

This document compares the Inertia implementation between Laravel (official) and our FastAPI adapter.

## Template Integration

### Laravel (Blade)
```blade
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    @viteReactRefresh
    @vite('resources/js/app.jsx')
    @inertiaHead
</head>
<body>
    @inertia
</body>
</html>
```

### FastAPI (Jinja2)
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    {{ vite()|safe }}
    <!-- Note: React refresh is automatically included in vite() -->
</head>
<body>
    <div id="app" data-page='{{ page }}'></div>
</body>
</html>
```

**Key Differences**:
- ✅ FastAPI: React Fast Refresh is **auto-included** in `vite()`, no separate directive needed
- ✅ FastAPI: `{{ vite() }}` is cleaner than separate `@viteReactRefresh` + `@vite()`
- ❌ FastAPI: No equivalent to `@inertiaHead` (for `<Head>` component) yet

## Vite Entry Configuration

### Laravel
```php
// Hardcoded in Blade template
@vite('resources/js/app.jsx')

// Multiple entries
@vite(['resources/js/app.js', 'resources/css/app.css'])
```

### FastAPI
```python
# Auto-detected from vite.config.ts
inertia = InertiaResponse()  # Reads: build.rollupOptions.input

# Manual override
inertia = InertiaResponse(vite_entry='frontend/app.tsx')

# Per-template override
{{ vite('admin/app.js')|safe }}
```

**Advantages**:
- ✅ **DRY principle**: Entry defined once in `vite.config.ts`
- ✅ **Type-safe**: Config file is authoritative source
- ✅ **Flexible**: Can override per-template if needed
- ❌ **Multiple entries**: Not yet supported (need multiple `vite()` calls)

## Creating Responses

### Laravel
```php
use Inertia\Inertia;

class EventsController extends Controller
{
    public function show(Event $event)
    {
        return Inertia::render('Event/Show', [
            'event' => $event->only('id', 'title', 'date'),
        ]);
    }
}
```

### FastAPI
```python
from inertia import InertiaDep

@app.get("/events/{event_id}")
async def show_event(event_id: int, inertia: InertiaDep):
    return inertia.render(
        'Event/Show',
        {'event': {'id': event.id, 'title': event.title, 'date': event.date}}
    )
```

**Very Similar!** The API is intentionally designed to match Laravel's.

## Validation Errors

### Laravel
```php
public function store(Request $request)
{
    $validated = $request->validate([
        'name' => 'required|max:255',
        'email' => 'required|email',
    ]);

    // On validation failure, automatically redirects back with errors
    User::create($validated);

    return Inertia::render('Users/Index');
}
```

### FastAPI
```python
@app.post("/users")
async def create_user(inertia: InertiaDep, user_data: dict):
    errors = validate_user(user_data)

    if errors:
        # Explicitly render with errors
        return inertia.render(
            'Users/Create',
            {'user': user_data},
            errors=errors
        )

    create_user(user_data)
    return inertia.render('Users/Index', {'users': get_users()})
```

**Key Differences**:
- Laravel: Automatic redirect on validation failure
- FastAPI: Explicit error handling (more Pythonic)
- Both: Return 422 status for Inertia XHR requests

## Shared Data

### Laravel
```php
// In HandleInertiaRequests middleware
public function share(Request $request): array
{
    return array_merge(parent::share($request), [
        'auth' => [
            'user' => $request->user(),
        ],
        'flash' => [
            'success' => fn () => $request->session()->get('success'),
            'error' => fn () => $request->session()->get('error'),
        ],
    ]);
}
```

### FastAPI
```python
# 🚧 NOT YET IMPLEMENTED
# Planned approach:

from inertia import InertiaMiddleware

app.add_middleware(
    InertiaMiddleware,
    shared_data={
        'auth': lambda request: {'user': get_current_user(request)},
        'flash': lambda request: get_flash_messages(request),
    }
)
```

## Partial Reloads

### Laravel
```php
return Inertia::render('Users/Index', [
    'users' => User::all(),
    'organizations' => fn () => Organization::all(), // Lazy evaluated
]);
```

### FastAPI
```python
# 🚧 NOT YET IMPLEMENTED
# Planned approach:

from inertia import lazy

return inertia.render('Users/Index', {
    'users': get_users(),
    'organizations': lazy(lambda: get_organizations()),  # Only loaded when requested
})
```

## Asset Versioning

### Laravel
```php
// In HandleInertiaRequests middleware
public function version(Request $request): ?string
{
    return parent::version($request);
}
```

### FastAPI
```python
# ✅ IMPLEMENTED
# Automatically generates version hash from manifest
# Returns 'dev' in development mode
# Returns hash of manifest.json in production

# 🚧 Version mismatch detection (409 Conflict) not yet implemented
```

## Feature Matrix

| Feature | Laravel | FastAPI | Notes |
|---------|---------|---------|-------|
| **Basic rendering** | ✅ | ✅ | Identical API |
| **Validation errors** | ✅ Auto | ✅ Manual | FastAPI more explicit |
| **Template directive** | ✅ `@vite()` | ✅ `{{ vite() }}` | FastAPI auto-includes React refresh |
| **Auto Vite config** | ✅ | ✅ | FastAPI reads from vite.config.ts |
| **Dev mode detection** | ✅ | ✅ | Both automatic |
| **Asset versioning** | ✅ | 🟡 Partial | Basic implementation done |
| **Version mismatch (409)** | ✅ | ❌ | To be implemented |
| **Shared data** | ✅ | ❌ | To be implemented |
| **Partial reloads** | ✅ | ❌ | To be implemented |
| **Lazy props** | ✅ | ❌ | To be implemented |
| **Deferred props** | ✅ | ❌ | To be implemented |
| **SSR support** | ✅ | ❌ | Not planned yet |
| **Testing helpers** | ✅ | 🟡 Partial | Basic test suite exists |
| **History encryption** | ✅ | ❌ | To be implemented |
| **Prefetching** | ✅ | ❌ | To be implemented |

## Advantages of FastAPI Implementation

1. **Simpler Vite integration**: Single `{{ vite() }}` function vs separate directives
2. **Auto-detection**: Reads entry from vite.config.ts (DRY principle)
3. **Type hints**: Better IDE support with Python type hints
4. **Explicit validation**: More Pythonic error handling
5. **Async support**: Native async/await for better performance

## Advantages of Laravel Implementation

1. **Mature ecosystem**: More battle-tested
2. **Automatic validation redirects**: Less boilerplate
3. **Middleware integration**: Built-in shared data support
4. **Complete feature set**: All Inertia features implemented
5. **Official support**: Maintained by Inertia core team

## Conclusion

The FastAPI adapter is **intentionally designed to match Laravel's API** while adding Python-specific improvements like:
- Better type safety
- Auto-configuration from vite.config
- Cleaner template integration

However, it's still **missing some advanced features** like shared data and partial reloads. These are planned for future releases.
