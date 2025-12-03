---
title: Server-Side Rendering
description: Enable SSR for improved SEO and faster initial page loads.
order: 8
section: Advanced
---

## Overview

Server-side rendering (SSR) allows your Inertia pages to be rendered on the server, providing better SEO and faster initial page loads. Cross-Inertia includes built-in SSR support.

## Setting up SSR

### 1. Create the SSR entry point

Create a `frontend/ssr.tsx` file:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import ReactDOMServer from 'react-dom/server'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })

export default function render(page: any) {
  return createInertiaApp({
    page,
    render: ReactDOMServer.renderToString,
    resolve: (name) => {
      const resolved = pages[`./pages/${name}.tsx`]
      if (!resolved) throw new Error(`Page ${name} not found`)
      return resolved
    },
    setup: ({ App, props }) => <App {...props} />,
  })
}
```

### 2. Configure Vite for SSR

Update your `vite.config.ts`:

```ts
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
  ssr: {
    noExternal: ['@inertiajs/react'],
  },
})
```

### 3. Build the SSR bundle

Add a build script to your `package.json`:

```json
{
  "scripts": {
    "build": "vite build",
    "build:ssr": "vite build --ssr frontend/ssr.tsx --outDir static/build/ssr"
  }
}
```

### 4. Configure Cross-Inertia for SSR

Update your FastAPI app to enable SSR:

```python
from inertia.fastapi import InertiaMiddleware
import inertia._core

inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    vite_entry="frontend/app.tsx",
    ssr_url="http://localhost:13714",  # SSR server URL
)
inertia._core._inertia_response = inertia_response
```

### 5. Run the SSR server

Start the SSR server using Bun:

```bash
bun run static/build/ssr/ssr.js
```

## SSR with Lifespan Management

For production deployments, you'll want to manage the SSR server lifecycle automatically. See the [SSR Lifespan](/docs/ssr-lifespan) guide for details.
