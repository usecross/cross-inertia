---
title: Configuration
description: Configure Cross-Inertia for your application.
order: 14
section: API Reference
---

## configure_inertia()

The `configure_inertia()` function is the single source of truth for all Cross-Inertia configuration. It sets up both template rendering and server lifecycle management with consistent settings.

```python
from inertia import configure_inertia

configure_inertia(
    vite_port="auto",
    vite_entry="frontend/app.tsx",
    ssr_enabled=True,
)
```

## Parameters

### Vite Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vite_port` | `int \| "auto"` | `5173` | Port for Vite dev server. Use `"auto"` to find an available port automatically. |
| `vite_host` | `str` | `"localhost"` | Host for Vite dev server. |
| `vite_entry` | `str` | `"frontend/app.tsx"` | Entry point for Vite (e.g., `"src/main.tsx"`). |
| `vite_command` | `str \| list[str]` | `"bun run dev"` | Command to start Vite dev server. Port is appended automatically. |
| `vite_timeout` | `float` | `30.0` | Timeout in seconds for Vite dev server startup. |

### Template Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `template_dir` | `str` | `"templates"` | Directory containing Jinja2 templates. |
| `manifest_path` | `str` | `"static/build/.vite/manifest.json"` | Path to Vite manifest file for production builds. |

### SSR Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ssr_enabled` | `bool` | `False` | Whether SSR is enabled. |
| `ssr_url` | `str` | `"http://127.0.0.1:13714"` | URL of the SSR server. |
| `ssr_command` | `str \| list[str]` | `"bun dist/ssr/ssr.js"` | Command to start the SSR server. |
| `ssr_timeout` | `float` | `10.0` | Timeout in seconds for SSR server startup. |
| `ssr_health_path` | `str` | `"/health"` | Health check path for SSR server. |

## Returns

Returns an `InertiaConfig` instance with all configuration values.

## Examples

### Basic Configuration

```python
from inertia import configure_inertia

# Uses sensible defaults
configure_inertia()
```

### Auto Port Selection

When running multiple projects or in CI environments, use `"auto"` to find an available port:

```python
from inertia import configure_inertia

configure_inertia(
    vite_port="auto",  # Finds unused port in range 5173-5273
)
```

### Full Configuration

```python
from inertia import configure_inertia

configure_inertia(
    # Vite settings
    vite_port=5188,
    vite_host="localhost",
    vite_entry="src/main.tsx",
    vite_command="npm run dev",
    vite_timeout=30.0,

    # Template settings
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",

    # SSR settings
    ssr_enabled=True,
    ssr_url="http://127.0.0.1:13714",
    ssr_command="node dist/ssr/ssr.js",
    ssr_timeout=10.0,
    ssr_health_path="/health",
)
```

### With Lifespan Management

Combine `configure_inertia()` with the experimental lifespan for automatic server management:

```python
from fastapi import FastAPI
from inertia import configure_inertia
from inertia.fastapi.experimental import inertia_lifespan

configure_inertia(
    vite_port="auto",
    ssr_enabled=True,
)

app = FastAPI(lifespan=inertia_lifespan)
```

## get_config()

Retrieve the current configuration. Returns a default configuration if `configure_inertia()` hasn't been called.

```python
from inertia import get_config

config = get_config()
print(config.vite_dev_url)  # http://localhost:5173
print(config.ssr_enabled)   # False
```

## InertiaConfig

The configuration dataclass with the following properties:

| Property | Description |
|----------|-------------|
| `vite_dev_url` | Full Vite dev server URL (e.g., `http://localhost:5173`) |
| `resolved_vite_port` | The actual port being used (resolves `"auto"`) |
| `ssr_health_url` | Full SSR health check URL |

## Template Variables

Your Jinja2 template has access to these variables:

| Variable | Description |
|----------|-------------|
| `page` | JSON-encoded page data for the `data-page` attribute |
| `vite()` | Function that returns Vite script/style tags |
| `head` | SSR head tags (when SSR is enabled) |
| `body` | SSR body content (when SSR is enabled) |

**Example template:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ view_data.page_title | default('My App') }}</title>
    {% if head %}{{ head | safe }}{% endif %}
    {{ vite() | safe }}
</head>
<body>
    {% if body %}
        {{ body | safe }}
    {% else %}
        <div id="app" data-page='{{ page | safe }}'></div>
    {% endif %}
</body>
</html>
```

## Vite Configuration

Cross-Inertia expects a standard Vite configuration:

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    manifest: true,
    outDir: 'static/build',
    rollupOptions: {
      input: 'frontend/app.tsx',
    },
  },
})
```

## Exceptions

### ManifestNotFoundError

Raised when the Vite manifest file is missing in production mode:

```python
from inertia import ManifestNotFoundError

try:
    # Render in production without building first
    return inertia.render("Home", {})
except ManifestNotFoundError:
    # Handle missing manifest - typically means you forgot to run `vite build`
    pass
```

## Migration from InertiaResponse

If you're upgrading from an older version that used `InertiaResponse` directly:

**Before (deprecated):**

```python
import inertia._core

inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    vite_dev_url="http://localhost:5173",
)
inertia._core._inertia_response = inertia_response
```

**After (recommended):**

```python
from inertia import configure_inertia

configure_inertia(
    template_dir="templates",
    vite_port=5173,
)
```

The new approach:
- Uses a public API instead of private internals
- Provides consistent configuration for both rendering and lifespan management
- Supports auto port selection
- Is the recommended pattern going forward
