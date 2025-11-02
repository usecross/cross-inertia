# Inertia Template Functions

The Inertia adapter provides custom Jinja2 functions that can be used in your templates, similar to Laravel's Blade directives.

## `vite()` Function

The `vite()` function generates the appropriate script and CSS tags for your Vite assets, automatically handling both development and production modes.

### Basic Usage

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {{ vite()|safe }}
</head>
<body>
    <div id="app" data-page='{{ page }}'></div>
</body>
</html>
```

### With Custom Entry Point

You can optionally specify a custom entry point (overriding the configured default):

```html
<!-- Use the default entry from configuration -->
{{ vite()|safe }}

<!-- Use a custom entry point -->
{{ vite('admin/app.js')|safe }}
```

### How It Works

**Development Mode** (when Vite dev server is running):
```html
<!-- Generated output: -->
<script type="module">
    import RefreshRuntime from "http://localhost:5173/@react-refresh"
    RefreshRuntime.injectIntoGlobalHook(window)
    window.$RefreshReg$ = () => {}
    window.$RefreshSig$ = () => (type) => type
    window.__vite_plugin_react_preamble_installed__ = true
</script>
<script type="module" src="http://localhost:5173/@vite/client"></script>
<script type="module" src="http://localhost:5173/frontend/app.tsx"></script>
```

**Production Mode** (after `npm run build`):
```html
<!-- Generated output: -->
<link rel="stylesheet" href="/static/build/assets/app.abc123.css">
<script type="module" src="/static/build/assets/app.xyz789.js"></script>
```

### Comparison with Laravel

| Laravel | FastAPI Inertia |
|---------|----------------|
| `@vite('resources/js/app.js')` | `{{ vite()|safe }}` |
| `@vite(['resources/js/app.js', 'resources/css/app.css'])` | Not yet supported (use multiple calls) |
| `@viteReactRefresh` | Automatic (included in `vite()`) |

### Backward Compatibility

For backward compatibility, the old `{{ vite_tags|safe }}` variable is still supported:

```html
<!-- Old way (still works): -->
{{ vite_tags|safe }}

<!-- New way (recommended): -->
{{ vite()|safe }}
```

## Configuration

The `vite()` function uses the configuration from `InertiaResponse`:

```python
from inertia import InertiaResponse

inertia_response = InertiaResponse(
    vite_dev_url="http://localhost:5173",  # Dev server URL
    manifest_path="static/build/.vite/manifest.json",  # Production manifest
    vite_entry="frontend/app.tsx",  # Default entry (auto-detected if None)
)
```

## Auto-Detection

If `vite_entry` is not specified, it will be automatically detected from your `vite.config.ts`:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      input: "frontend/app.tsx",  // ← Automatically detected
    },
  },
});
```

This means your Python code and Vite config stay in sync automatically!

## Multiple Entry Points

If you have multiple entry points (e.g., separate admin panel), you can call `vite()` multiple times:

```html
<!-- Main app -->
{{ vite('frontend/app.tsx')|safe }}

<!-- Admin app (on admin pages) -->
{% if is_admin_page %}
    {{ vite('frontend/admin.tsx')|safe }}
{% endif %}
```

## React Fast Refresh

React Fast Refresh is automatically included in development mode. You don't need to add any special directives like Laravel's `@viteReactRefresh` - it's built into the `vite()` function.

## Implementation Note

The `vite()` function is registered as a Jinja2 global function during `InertiaResponse` initialization:

```python
# This happens automatically
self.templates.env.globals["vite"] = self._vite_template_function
```

This makes it available in all templates rendered by Inertia.
