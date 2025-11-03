# Inertia.js FastAPI Adapter

[![Tests](https://github.com/patrick91/cross-inertia/actions/workflows/test.yml/badge.svg)](https://github.com/patrick91/cross-inertia/actions/workflows/test.yml)
[![Lint](https://github.com/patrick91/cross-inertia/actions/workflows/lint.yml/badge.svg)](https://github.com/patrick91/cross-inertia/actions/workflows/lint.yml)
[![PyPI version](https://badge.fury.io/py/cross-inertia.svg)](https://badge.fury.io/py/cross-inertia)
[![Python Versions](https://img.shields.io/pypi/pyversions/cross-inertia.svg)](https://pypi.org/project/cross-inertia/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python adapter for using [Inertia.js](https://inertiajs.com/) with FastAPI.

**[📚 Documentation](https://inertia.patrick.wtf)** | **[🚀 Quick Start](#quick-start)** | **[🗺️ Roadmap](./ROADMAP.md)**

## Features

- ✅ Full Inertia.js protocol support
- ✅ Vite integration (dev & production)
- ✅ Auto-detection of Vite entry point from vite.config.ts/js
- ✅ Asset versioning for cache busting
- ✅ Validation error handling (422 responses)
- ✅ History encryption for sensitive data
- ✅ External redirects (OAuth, payments, etc.)
- ✅ Partial reloads & shared data
- ✅ TypeScript support

## Installation

```bash
# Install from PyPI using uv (recommended)
uv pip install cross-inertia

# Or using pip
pip install cross-inertia

# Or install from source
uv pip install -e .
```

## Try the Demo

We have a full-featured cat adoption demo app in `examples/fastapi/`:

```bash
# Using just (recommended)
just demo-install   # Install dependencies
just demo-fastapi   # Run the demo

# Or manually
cd examples/fastapi
bun install
./run-dev.sh
```

Visit http://127.0.0.1:8000 to see Inertia.js + FastAPI in action!

## Quick Start

### 1. Basic Setup

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

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
from fastapi import FastAPI, Request, Depends
from inertia.fastapi import InertiaResponse, Inertia

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
    from lia import StarletteRequestAdapter
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

## External Redirects

Use `inertia.location()` to redirect to external websites or non-Inertia pages:

```python
@app.get("/auth/github")
async def github_oauth(inertia: InertiaDep):
    """Redirect to GitHub OAuth"""
    oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    return inertia.location(oauth_url)

@app.get("/shelter/{id}/directions")
async def get_directions(id: int, inertia: InertiaDep):
    """Redirect to Google Maps"""
    shelter = get_shelter(id)
    maps_url = f"https://maps.google.com/?q={shelter.address}"
    return inertia.location(maps_url)
```

This returns a `409 Conflict` response with `X-Inertia-Location` header, which the client automatically follows with a full page navigation.

## History Encryption

Protect sensitive data in browser history by encrypting page state. This prevents users from viewing sensitive information after logging out by pressing the back button.

```python
# Encrypt sensitive pages
@app.get("/account/transactions")
async def transactions(inertia: InertiaDep):
    inertia.encrypt_history()  # Enable encryption
    return inertia.render("Transactions", {
        "balance": user.balance,
        "transactions": user.get_transactions()
    })

# Clear encrypted history on logout
@app.post("/logout")
async def logout(inertia: InertiaDep):
    clear_user_session()
    inertia.clear_history()  # Rotate encryption keys
    return inertia.render("Login", {})
```

**How it works:**
- Uses browser's Web Crypto API (AES-GCM encryption)
- Encryption keys stored in sessionStorage
- `clear_history()` rotates keys, making old history unreadable
- Only works over HTTPS (except localhost)

**Use cases:** Banking apps, healthcare (HIPAA), admin panels, any sensitive data

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
| **Asset version mismatch (409)** | ✅ | ✅ | - |
| **Partial reloads** | ✅ | ✅ | - |
| **Shared data** | ✅ | ✅ | - |
| **External redirects** | ✅ | ✅ | - |
| **History encryption** | ✅ | ✅ | - |
| Lazy props | ✅ | ⏳ Planned | 🟡 Medium |
| Deferred props | ✅ | ⏳ Planned | 🟡 Medium |
| Merging props | ✅ | ⏳ Planned | 🟡 Medium |
| Error bags | ✅ | ⏳ Planned | 🟢 Low |
| Prefetching | ✅ | ⏳ Planned | 🟢 Low |
| SSR | ✅ | ❌ Not planned | - |

**See [ROADMAP.md](./ROADMAP.md) for detailed implementation plans and progress tracking.**

## Current Status

**Version:** v0.2.0 "Production Ready"

This adapter implements all production-critical Inertia features and is **ready for production use**.

**Production-ready features:**
- ✅ Basic page rendering
- ✅ Form submissions with validation
- ✅ Navigation between pages
- ✅ Development with Vite HMR
- ✅ Asset version mismatch handling (409 Conflict)
- ✅ Partial reloads for performance
- ✅ Shared data (auth, flash messages)
- ✅ External redirects (OAuth, payments)
- ✅ History encryption (sensitive data protection)

**Coming soon:**
- ⏳ Lazy props evaluation
- ⏳ Deferred props
- ⏳ Merging props (infinite scroll)

## Contributing

Contributions are very welcome! This adapter aims to match the Laravel adapter's feature set.

**How to contribute:**

1. Check [GitHub Issues](https://github.com/patrick91/cross-inertia/issues) for open tasks
2. Pick a feature (look for `good first issue` or `high-priority` labels)
3. Read the linked Inertia.js documentation
4. Implement following existing patterns
5. Write tests and update documentation
6. Submit a PR!

**See [ROADMAP.md](./ROADMAP.md) for the full project roadmap and milestone planning.**

## License

MIT
