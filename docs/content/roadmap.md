# Inertia FastAPI Adapter - Feature Roadmap

This document tracks the implementation status of all Inertia.js features in the FastAPI adapter, compared to the official [Inertia.js specification](https://inertiajs.com/).

## Current Version: 0.1.0

---

## ✅ Implemented Features

### Core Protocol
- [x] **X-Inertia header detection** - Distinguishes between initial loads and XHR requests
- [x] **JSON responses for Inertia requests** - Returns page object as JSON
- [x] **HTML responses for initial loads** - Returns full HTML with `data-page` attribute
- [x] **Page object structure** - Includes `component`, `props`, `url`, `version`
- [x] **Vary: X-Inertia header** - Prevents browser caching issues

### Validation & Errors
- [x] **422 status code for validation errors** - Proper error handling for Inertia requests
- [x] **Errors in props** - Validation errors passed to components via `props.errors`
- [x] **Error display in both JSON and HTML** - Works for XHR and initial loads

### Vite Integration
- [x] **Auto Vite entry detection** - Reads from `vite.config.ts`/`.js` automatically
- [x] **Dev/Production mode detection** - Auto-detects if Vite dev server is running
- [x] **React Fast Refresh** - Automatically included in dev mode
- [x] **Template function `{{ vite() }}`** - Laravel-like directive for asset loading
- [x] **Custom entry point override** - `{{ vite('custom.js') }}` per-template
- [x] **Manifest parsing** - Reads `.vite/manifest.json` for production builds

### Asset Management
- [x] **Asset versioning (basic)** - Returns version hash for cache busting
- [x] **Dev mode version** - Returns 'dev' string in development
- [x] **Production version** - Hash based on manifest contents

### Developer Experience
- [x] **Type hints** - Full Python type annotations
- [x] **Lazy singleton** - Prevents import-time initialization issues
- [x] **FastAPI dependency injection** - `InertiaDep` for easy usage
- [x] **Backward compatibility** - Old `{{ vite_tags }}` still works

---

## 🔴 High Priority - Critical for Production

### Asset Version Mismatch Handling
**Status:** Not Implemented
**Priority:** Critical
**Effort:** Medium (2-3 hours)
**Blocking:** Production deployments with rolling updates

#### What's Needed:
```python
# Check X-Inertia-Version header
incoming_version = request.headers.get('X-Inertia-Version')
current_version = self.get_asset_version()

if incoming_version and incoming_version != current_version:
    # Return 409 Conflict for GET requests
    return Response(
        status_code=409,
        headers={
            'X-Inertia-Location': str(request.url)
        }
    )
```

#### Why Important:
- Prevents users from using stale JavaScript after deployments
- Forces full page reload when assets change
- **Required for production apps with frequent deployments**

#### References:
- [Inertia Protocol - Asset Versioning](https://inertiajs.com/the-protocol#asset-versioning)
- See: `tests/test_asset_versioning.py` (currently skipped)

---

### Partial Reloads
**Status:** Not Implemented
**Priority:** High
**Effort:** High (6-8 hours)
**Use Case:** Performance optimization for data-heavy pages

#### What's Needed:
1. Check `X-Inertia-Partial-Data` header for requested props
2. Check `X-Inertia-Partial-Component` to verify same component
3. Filter props to only include requested keys
4. Support `Inertia::optional()` and `Inertia::always()` helpers

```python
# Server-side implementation
def render(self, request: Request, component: str, props: dict):
    partial_data = request.headers.get('X-Inertia-Partial-Data')
    partial_component = request.headers.get('X-Inertia-Partial-Component')

    # Only filter if requesting same component
    if partial_data and partial_component == component:
        requested_keys = partial_data.split(',')
        props = {k: v for k, v in props.items() if k in requested_keys}

    return self._render_response(component, props)
```

#### Why Important:
- **Major performance boost** for pages with multiple data sources
- Reduces server load by not computing unnecessary data
- Reduces response size and network transfer time
- **Essential for admin panels, dashboards, and data tables**

#### Example Use Cases:
- User list with filters (reload users, keep categories)
- Dashboard with refresh (reload stats, keep layout data)
- Product catalog with search (reload results, keep filters)

#### References:
- [Inertia Protocol - Partial Reloads](https://inertiajs.com/the-protocol#partial-reloads)
- [Partial Reloads Guide](https://inertiajs.com/partial-reloads)
- See: `tests/test_partial_reloads.py` (currently skipped)

---

### Missing Page Object Fields
**Status:** Not Implemented
**Priority:** High
**Effort:** Low (1-2 hours)
**Blocking:** Advanced features

#### What's Needed:
Add these fields to page object when applicable:
```python
page_data = {
    "component": component,
    "props": props,
    "url": str(request.url.path),
    "version": self.get_asset_version(),

    # New fields:
    "encryptHistory": False,  # For sensitive data
    "clearHistory": False,     # Clear encrypted history
    "mergeProps": [],          # Props to merge on navigation
    "prependProps": [],        # Props to prepend
    "deepMergeProps": [],      # Props to deep merge
    "scrollProps": {},         # Infinite scroll config
    "deferredProps": {},       # Lazy-loaded props
}
```

#### Why Important:
- Required for infinite scroll
- Required for deferred props
- Required for history encryption
- **Needed before implementing those features**

#### References:
- [Inertia Protocol - Page Object](https://inertiajs.com/the-protocol#the-page-object)

---

## 🟡 Medium Priority - Important Features

### Shared Data Middleware
**Status:** Not Implemented
**Priority:** Medium
**Effort:** Medium (4-5 hours)
**Use Case:** Auth, flash messages, global data

#### What's Needed:
```python
from starlette.middleware.base import BaseHTTPMiddleware

class InertiaMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, shared_data: dict):
        super().__init__(app)
        self.shared_data = shared_data

    async def dispatch(self, request, call_next):
        # Inject shared data into Inertia context
        response = await call_next(request)
        return response

# Usage:
app.add_middleware(InertiaMiddleware, shared_data={
    'auth': lambda req: {'user': get_user(req)},
    'flash': lambda req: get_flash(req),
})
```

#### Why Important:
- Reduces boilerplate (don't repeat auth/user in every route)
- Consistent data structure across all pages
- **Essential for authentication and flash messages**

#### References:
- [Shared Data](https://inertiajs.com/shared-data)

---

### External Redirects
**Status:** Not Implemented
**Priority:** Medium
**Effort:** Low (1-2 hours)
**Use Case:** OAuth, external links, logout

#### What's Needed:
```python
def location(url: str) -> Response:
    """Redirect to external URL via 409 + X-Inertia-Location"""
    return Response(
        status_code=409,
        headers={
            'X-Inertia-Location': url
        }
    )

# Usage:
return inertia.location('https://github.com/login')
```

#### Why Important:
- OAuth flows require external redirects
- Logout should redirect to external page
- Third-party integrations

#### References:
- [Redirects - External](https://inertiajs.com/redirects#external-redirects)

---

### Lazy Props Evaluation
**Status:** Not Implemented
**Priority:** Medium
**Effort:** Medium (3-4 hours)
**Use Case:** Performance optimization

#### What's Needed:
```python
class LazyProp:
    def __init__(self, callback):
        self.callback = callback

    def evaluate(self):
        return self.callback()

def lazy(callback):
    return LazyProp(callback)

# Usage:
return inertia.render('Users/Index', {
    'users': get_users(),  # Always evaluated
    'companies': lazy(lambda: get_companies()),  # Only if needed
})
```

#### Why Important:
- Works with partial reloads to avoid unnecessary computation
- **Can dramatically reduce server response time**
- Only evaluates data that's actually requested

#### References:
- [Partial Reloads - Lazy Evaluation](https://inertiajs.com/partial-reloads#lazy-data-evaluation)

---

### Deferred Props
**Status:** Not Implemented
**Priority:** Medium
**Effort:** High (6-8 hours)
**Use Case:** Load slow data after initial render

#### What's Needed:
```python
def defer(callback, group='default'):
    return DeferredProp(callback, group)

# Usage:
return inertia.render('Dashboard', {
    'user': get_user(),  # Fast
    'analytics': defer(lambda: slow_analytics_call()),  # Loaded later
})
```

#### Why Important:
- Initial page loads faster
- Progressive data loading
- **Better perceived performance for slow API calls**

#### References:
- [Deferred Props](https://inertiajs.com/deferred-props)

---

### Merging Props (Infinite Scroll)
**Status:** Not Implemented
**Priority:** Medium
**Effort:** Medium (4-5 hours)
**Use Case:** Infinite scroll, live feeds

#### What's Needed:
Support for `mergeProps`, `prependProps`, `deepMergeProps` in page object.

```python
return inertia.render('Feed', {
    'posts': get_posts(page),
}, merge=['posts'])  # Append new posts to existing
```

#### Why Important:
- Required for infinite scroll
- Required for live-updating feeds
- **Common pattern in modern apps**

#### References:
- [Merging Props](https://inertiajs.com/merging-props)
- [Infinite Scroll](https://inertiajs.com/infinite-scroll)

---

## 🟢 Low Priority - Nice to Have

### Error Bags
**Status:** Not Implemented
**Priority:** Low
**Effort:** Low (1-2 hours)
**Use Case:** Multiple forms on one page

#### What's Needed:
Check `X-Inertia-Error-Bag` header and scope errors accordingly.

```python
error_bag = request.headers.get('X-Inertia-Error-Bag', 'default')
props['errors'][error_bag] = validation_errors
```

#### Why Important:
- Prevents error collisions on multi-form pages
- Better UX for complex forms

#### References:
- [Validation - Error Bags](https://inertiajs.com/validation#error-bags)

---

### Prefetch Support
**Status:** Not Implemented
**Priority:** Low
**Effort:** Low (2-3 hours)
**Use Case:** Performance optimization

#### What's Needed:
Detect `Purpose: prefetch` header and handle accordingly.

```python
if request.headers.get('Purpose') == 'prefetch':
    # Return lightweight/cached response
    pass
```

#### Why Important:
- Preloads pages on hover
- Instant navigation feel
- **Great for marketing sites and blogs**

#### References:
- [Prefetching](https://inertiajs.com/prefetching)

---

### History Encryption
**Status:** Not Implemented
**Priority:** Low
**Effort:** Medium (3-4 hours)
**Use Case:** Sensitive data in history

#### What's Needed:
Support `encryptHistory` and `clearHistory` page object fields.

```python
return inertia.render('Payments', {
    'payment': payment_data
}, encrypt_history=True)
```

#### Why Important:
- Prevents sensitive data in browser history
- Compliance requirements (PCI, HIPAA)
- **Only needed for apps handling sensitive data**

#### References:
- [History Encryption](https://inertiajs.com/history-encryption)

---

### Polling
**Status:** Not Implemented
**Priority:** Low
**Effort:** Low (Client-side mostly)
**Use Case:** Auto-refresh data

#### Why Important:
- Real-time updates without WebSockets
- Dashboard auto-refresh
- **Mostly client-side implementation**

#### References:
- [Polling](https://inertiajs.com/polling)

---

## ⚪ Not Planned / Out of Scope

### Server-Side Rendering (SSR)
**Status:** Not Planned
**Reason:** Requires Node.js runtime, complex setup

SSR would require:
- Node.js runtime alongside Python
- V8 isolates or similar
- Significant complexity

**Alternative:** Use meta tags and prerendering for SEO.

#### References:
- [Server-Side Rendering](https://inertiajs.com/server-side-rendering)

---

### Multiple Client Framework Support
**Status:** Out of Scope
**Reason:** Client-side adapters maintained by Inertia core team

The server adapter is framework-agnostic - it works with any Inertia client (React, Vue, Svelte). Supporting specific frameworks is handled client-side.

---

## 📊 Implementation Progress

### By Priority
- 🔴 High Priority: 3/3 features remaining
- 🟡 Medium Priority: 5/5 features remaining
- 🟢 Low Priority: 4/4 features remaining

### By Complexity
- Low Effort (< 3h): 5 features
- Medium Effort (3-6h): 5 features
- High Effort (> 6h): 2 features

### Overall Completion
- ✅ Implemented: ~60% of core features
- 🚧 In Progress: 0%
- ⏳ Planned: ~40% remaining

---

## 🎯 Recommended Implementation Order

When ready to complete the adapter, implement in this order:

1. **Asset version mismatch** (Critical, Low effort) - Blocks production use
2. **Page object fields** (High, Low effort) - Enables other features
3. **External redirects** (Medium, Low effort) - Quick win
4. **Shared data middleware** (Medium, Medium effort) - High value
5. **Lazy props** (Medium, Medium effort) - Pairs with #6
6. **Partial reloads** (High, High effort) - Big performance win
7. **Deferred props** (Medium, High effort) - Performance boost
8. **Merging props** (Medium, Medium effort) - For infinite scroll
9. **Error bags** (Low, Low effort) - Polish
10. **Prefetch support** (Low, Low effort) - Polish
11. **History encryption** (Low, Medium effort) - If needed
12. **Polling** (Low, Low effort) - Client-side mostly

---

## 🤝 Contributing

Want to help implement these features? Here's how:

1. **Pick a feature** from the roadmap
2. **Read the Inertia.js docs** linked in references
3. **Check the test file** (if marked as skipped) for expected behavior
4. **Implement the feature** following the existing code patterns
5. **Write/update tests** to verify the implementation
6. **Update this roadmap** to mark the feature as implemented

### Guidelines
- Match Laravel adapter behavior where possible
- Include type hints and docstrings
- Add tests for the feature
- Update documentation (README.md, TEMPLATE_FUNCTIONS.md, etc.)

---

## 📚 Resources

- [Inertia.js Official Docs](https://inertiajs.com/)
- [The Protocol Specification](https://inertiajs.com/the-protocol)
- [Laravel Adapter Source](https://github.com/inertiajs/inertia-laravel)
- [React Adapter Source](https://github.com/inertiajs/inertia/tree/master/packages/react)

---

## 📝 Version History

- **0.1.0** (Current) - Initial implementation with core features
- **0.2.0** (Planned) - Asset version mismatch + partial reloads
- **0.3.0** (Planned) - Shared data + lazy props
- **1.0.0** (Goal) - Feature parity with Laravel adapter (minus SSR)

---

Last Updated: November 2024
