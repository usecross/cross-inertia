# Inertia.js FastAPI Adapter

A Python adapter for using [Inertia.js](https://inertiajs.com/) with FastAPI.

## Features

- ✅ Full Inertia.js protocol support
- ✅ Vite integration (dev & production)
- ✅ Auto-detection of Vite entry point from vite.config.ts/js
- ✅ Asset versioning for cache busting
- ✅ Validation error handling (422 responses)
- ✅ TypeScript support

## Installation

```bash
# This package (when published)
pip install inertia-fastapi

# Or install from source
pip install -e .
```

## Quick Start

### 1. Basic Setup

```python
from fastapi import FastAPI
from inertia import InertiaDep

app = FastAPI()

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render(
        "Home",
        {
            "message": "Hello from Inertia!"
        }
    )
```

### 2. Custom Configuration

If you need to customize the Inertia configuration (e.g., different template directory or Vite settings):

```python
from fastapi import FastAPI, Request
from inertia import InertiaResponse, Inertia

# Create custom InertiaResponse instance
inertia_response = InertiaResponse(
    template_dir="my_templates",
    vite_dev_url="http://localhost:5173",
    manifest_path="dist/.vite/manifest.json",
    vite_entry="src/main.tsx",  # Optional: auto-detected from vite.config
    vite_config_path="vite.config.ts"  # Optional: defaults to vite.config.ts
)

app = FastAPI()

def get_custom_inertia(request: Request) -> Inertia:
    return Inertia(request, inertia_response)

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
| `vite_entry` | `str \| None` | `None` | Vite entry point (auto-detected from config if None) |
| `vite_config_path` | `str` | `"vite.config.ts"` | Path to vite.config.ts/js for auto-detection |

### Auto-Detection of Vite Entry

By default, the adapter will attempt to read your `vite.config.ts` (or `.js`) file and extract the entry point from:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      input: "frontend/app.tsx",  // ← Auto-detected
    },
  },
});
```

This means you don't need to specify `vite_entry` manually - it will match your Vite configuration automatically!

## Root Template

Create a template file (default: `templates/app.html`):

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

The `{{ vite() }}` function will automatically include:
- React Fast Refresh scripts (dev mode)
- Vite client scripts (dev mode)
- Your entry point script
- Built CSS and JS files (production mode)

### Using Custom Entry Points

```html
<!-- Use default entry (from config/auto-detection) -->
{{ vite()|safe }}

<!-- Use custom entry point -->
{{ vite('admin/app.js')|safe }}
```

**Backward compatibility**: The old `{{ vite_tags|safe }}` variable is still supported.

## Validation Errors

Validation errors are automatically handled:

```python
@app.post("/users")
async def create_user(inertia: InertiaDep):
    errors = validate_user(request_data)

    if errors:
        # Returns 422 status for Inertia requests
        return inertia.render(
            "Users/Create",
            {"user": request_data},
            errors=errors
        )

    # Create user...
    return inertia.render("Users/Show", {"user": new_user})
```

## Development vs Production

The adapter automatically detects whether Vite dev server is running:

- **Dev mode**: Includes Vite dev server scripts and React Fast Refresh
- **Production mode**: Reads from manifest.json and includes built assets

No configuration changes needed - it just works!

## Feature Status

| Feature | Laravel Inertia | FastAPI Inertia | Priority |
|---------|----------------|-----------------|----------|
| Basic protocol | ✅ | ✅ | - |
| Template function `{{ vite() }}` | ✅ `@vite` | ✅ | - |
| Auto Vite entry detection | ✅ | ✅ | - |
| Dev/Prod mode detection | ✅ | ✅ | - |
| Validation errors (422) | ✅ | ✅ | - |
| Asset versioning (basic) | ✅ | ✅ | - |
| **Asset version mismatch (409)** | ✅ | ⏳ Planned | 🔴 High |
| **Partial reloads** | ✅ | ⏳ Planned | 🔴 High |
| **Shared data** | ✅ | ⏳ Planned | 🟡 Medium |
| **External redirects** | ✅ | ⏳ Planned | 🟡 Medium |
| Lazy props | ✅ | ⏳ Planned | 🟡 Medium |
| Deferred props | ✅ | ⏳ Planned | 🟡 Medium |
| Merging props | ✅ | ⏳ Planned | 🟡 Medium |
| Error bags | ✅ | ⏳ Planned | 🟢 Low |
| Prefetching | ✅ | ⏳ Planned | 🟢 Low |
| History encryption | ✅ | ⏳ Planned | 🟢 Low |
| SSR | ✅ | ❌ Not planned | - |

**See [ROADMAP.md](./ROADMAP.md) for detailed implementation plans and progress tracking.**

## Current Status

**Version:** 0.1.0 (Alpha)

This adapter implements ~60% of core Inertia features and is **suitable for simple applications**.

**Production-ready for:**
- ✅ Basic page rendering
- ✅ Form submissions with validation
- ✅ Navigation between pages
- ✅ Development with Vite HMR

**Not yet ready for:**
- ❌ Production deployments with rolling updates (no asset version mismatch handling)
- ❌ High-performance data tables (no partial reloads)
- ❌ Complex applications with shared data requirements

## Contributing

Contributions are very welcome! This adapter aims to match the Laravel adapter's feature set.

**How to contribute:**

1. Check [ROADMAP.md](./ROADMAP.md) for planned features
2. Pick a feature (high priority ones marked with 🔴)
3. Read the linked Inertia.js documentation
4. Implement following existing patterns
5. Write tests and update documentation
6. Submit a PR!

**Priority areas:**
- 🔴 Asset version mismatch (409 Conflict) - Critical for production
- 🔴 Partial reloads - Major performance feature
- 🟡 Shared data middleware - Essential for auth/flash messages

## License

MIT
