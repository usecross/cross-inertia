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

export default function render(page: any) {
  return createInertiaApp({
    page,
    render: ReactDOMServer.renderToString,
    setup: ({ App, props }) => <App {...props} />,
  })
}
```

The `@inertiajs/vite` plugin automatically handles page resolution for SSR, just like it does for the client entry point.

### 2. Configure Vite for SSR

Update your `vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import inertia from '@inertiajs/vite'

export default defineConfig({
  plugins: [react(), inertia()],
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
from cross_inertia import configure_inertia

configure_inertia(
    vite_entry="frontend/app.tsx",
    ssr_enabled=True,
)
```

### 5. Run the SSR server

Start the SSR server using Bun:

```bash
bun run static/build/ssr/ssr.js
```

## SSR with Lifespan Management

For production deployments, you'll want to manage the SSR server lifecycle automatically. See the [SSR Lifespan](/docs/ssr-lifespan) guide for details.
