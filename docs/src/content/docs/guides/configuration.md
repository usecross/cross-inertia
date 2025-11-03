---
title: Configuration
description: Configure Cross-Inertia to match your project structure
---

Cross-Inertia uses sensible defaults that work out of the box, but you can customize the configuration to match your project structure.

## Default Configuration

By default, Cross-Inertia uses these settings:

- **Template directory**: `templates/`
- **Template file**: `app.html`
- **Vite dev server**: `http://localhost:5173`
- **Manifest path**: `static/build/.vite/manifest.json`
- **Vite config path**: `vite.config.ts` (or `.js`)

## Using Default Configuration

The simplest way to use Cross-Inertia is with the default configuration using `InertiaDep`:

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello World"
    })
```

## Custom Configuration

If you need to customize settings, create a custom `InertiaResponse` instance:

```python
from fastapi import FastAPI, Request, Depends
from inertia.fastapi import InertiaResponse, Inertia
from lia import StarletteRequestAdapter

# Create custom instance
inertia_response = InertiaResponse(
    template_dir="my_templates",
    vite_dev_url="http://localhost:5174",
    manifest_path="dist/.vite/manifest.json",
    vite_entry="frontend/main.tsx",  # Optional: auto-detected
    vite_config_path="vite.config.ts"  # Optional
)

app = FastAPI()

def get_custom_inertia(request: Request) -> Inertia:
    adapter = StarletteRequestAdapter(request)
    return Inertia(request, adapter, inertia_response)

@app.get("/")
async def home(inertia: Inertia = Depends(get_custom_inertia)):
    return inertia.render("Home", {"message": "Hello!"})
```

## Configuration Options

### InertiaResponse Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `template_dir` | `str` | `"templates"` | Directory containing your root HTML template |
| `vite_dev_url` | `str` | `"http://localhost:5173"` | Vite dev server URL |
| `manifest_path` | `str` | `"static/build/.vite/manifest.json"` | Path to Vite manifest file (production) |
| `vite_entry` | `str \| None` | `None` | Vite entry point (auto-detected if None) |
| `vite_config_path` | `str` | `"vite.config.ts"` | Path to vite.config for auto-detection |

## Vite Entry Point Auto-Detection

Cross-Inertia automatically reads your `vite.config.ts` (or `.js`) and extracts the entry point:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      input: "frontend/app.tsx",  // Auto-detected
    },
  },
});
```

This means you don't need to specify `vite_entry` manually - it stays in sync with your Vite configuration.

### Manual Entry Point

If you prefer to specify the entry point manually or use a different config file location:

```python
inertia_response = InertiaResponse(
    vite_entry="src/main.tsx",
    vite_config_path="frontend/vite.config.ts"
)
```

## Root Template

Create your root template at `{template_dir}/app.html`:

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

### Custom Entry Points

You can use different entry points in different templates:

```html
<!-- Default entry point -->
{{ vite()|safe }}

<!-- Custom entry point -->
{{ vite('admin/app.js')|safe }}
```

### Backward Compatibility

The old `{{ vite_tags|safe }}` variable is still supported but deprecated:

```html
<!-- Old style (still works) -->
{{ vite_tags|safe }}

<!-- New style (recommended) -->
{{ vite()|safe }}
```

## Development vs Production

Cross-Inertia automatically detects whether Vite dev server is running:

### Development Mode

When Vite dev server is accessible:
- Includes Vite client scripts
- Enables React Fast Refresh
- Loads assets from dev server
- Hot module replacement works automatically

### Production Mode

When Vite dev server is not running:
- Reads from `manifest.json`
- Includes built CSS and JS files
- Serves optimized production assets

No configuration changes needed - it just works!

## Static Files

In production, you need to serve your built assets. With FastAPI:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

Make sure your Vite build output directory matches the static files directory:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: "static/build",
    manifest: true,
  },
});
```

## Multiple Vite Entry Points

For applications with multiple frontends (e.g., main app + admin panel):

```python
# Create separate instances for each frontend
main_inertia = InertiaResponse(
    template_dir="templates",
    vite_entry="frontend/app.tsx"
)

admin_inertia = InertiaResponse(
    template_dir="templates",
    vite_entry="frontend/admin.tsx"
)

def get_main_inertia(request: Request) -> Inertia:
    adapter = StarletteRequestAdapter(request)
    return Inertia(request, adapter, main_inertia)

def get_admin_inertia(request: Request) -> Inertia:
    adapter = StarletteRequestAdapter(request)
    return Inertia(request, adapter, admin_inertia)

@app.get("/")
async def home(inertia: Inertia = Depends(get_main_inertia)):
    return inertia.render("Home", {})

@app.get("/admin")
async def admin(inertia: Inertia = Depends(get_admin_inertia)):
    return inertia.render("Admin/Dashboard", {})
```

## Next Steps

- [Shared Data](/guides/shared-data/) - Share data across all pages
- [Validation Errors](/guides/validation-errors/) - Handle form validation
- [External Redirects](/guides/external-redirects/) - Redirect to external URLs
