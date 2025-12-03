---
title: Configuration
description: Configure Cross-Inertia for your application.
order: 14
section: API Reference
---

## InertiaResponse

The `InertiaResponse` class configures how Inertia renders pages.

```python
import inertia._core

inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    vite_entry="frontend/app.tsx",
    vite_dev_url="http://localhost:5173",
    ssr_url="http://localhost:13714",
)

# Set as the global Inertia response
inertia._core._inertia_response = inertia_response
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_dir` | `str` | Directory containing Jinja2 templates |
| `manifest_path` | `str` | Path to Vite's manifest.json |
| `vite_entry` | `str` | Entry point for Vite |
| `vite_dev_url` | `str \| None` | Vite dev server URL (None in production) |
| `ssr_url` | `str \| None` | SSR server URL (None to disable SSR) |
| `template_name` | `str` | Template filename (default: "app.html") |

## Template Variables

Your Jinja2 template has access to these variables:

| Variable | Description |
|----------|-------------|
| `page` | JSON-encoded page data for the `data-page` attribute |
| `vite()` | Function that returns Vite script/style tags |

**Example template:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ view_data.page_title | default('My App') }}</title>
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>
```

## Environment Configuration

Common configuration patterns:

### Development

```python
import sys

DEBUG = "dev" in sys.argv

inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    vite_entry="frontend/app.tsx",
    vite_dev_url="http://localhost:5173" if DEBUG else None,
)
```

### Production with SSR

```python
inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    vite_entry="frontend/app.tsx",
    vite_dev_url=None,
    ssr_url="http://localhost:13714",
)
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
