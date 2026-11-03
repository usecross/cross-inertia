---
title: Server-Side Rendering
description: Enable SSR for improved SEO and faster initial page loads.
order: 8
section: Advanced
---

## Overview

Server-side rendering (SSR) pre-renders your JavaScript pages on the server, allowing visitors to receive fully rendered HTML. This improves SEO and provides faster initial page loads.

With the `@inertiajs/vite` plugin, SSR setup is streamlined: the plugin reuses your existing `app.tsx` entry point for both client and SSR rendering, and during development, it handles SSR automatically without needing a separate Node.js server.

> **Note:** SSR requires Node.js 22+ to run the production SSR server.

## Setting up SSR

### 1. Vite Plugin (Recommended)

The `@inertiajs/vite` plugin is already configured in your `vite.config.ts`. It automatically handles SSR without any additional configuration:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import inertia from '@inertiajs/vite'

export default defineConfig({
  plugins: [react(), inertia()],
  // ... rest of your config
})
```

The plugin detects your SSR entry point automatically and enables SSR development mode out of the box.

### 2. Update Build Script

Update your `package.json` to build both client and SSR bundles:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build && vite build --ssr"
  }
}
```

### 3. Configure Cross-Inertia for SSR

Enable SSR in your FastAPI application:

```python
from cross_inertia import configure_inertia

configure_inertia(
    vite_entry="frontend/app.tsx",
    ssr_enabled=True,
)
```

### 4. Development

During development, just run Vite as usual. The plugin handles SSR automatically with hot module replacement:

```bash
npm run dev
# or
bun run dev
```

No separate SSR server needed in development!

### 5. Production

For production, build both bundles and start the SSR server:

```bash
# Build client and SSR bundles
npm run build

# Start your SSR server (see SSR Lifespan guide for production management)
bun run static/build/ssr/app.js
```

## Customizing with withApp

The plugin reuses your `app.tsx` entry point for SSR, so any customizations you make with `withApp` apply to both client and SSR rendering:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

createInertiaApp({
  withApp(app, { ssr }) {
    // Optionally apply different logic for SSR vs client
    if (!ssr) {
      // Client-only setup
    }
    
    return (
      <QueryClientProvider client={queryClient}>
        {app}
      </QueryClientProvider>
    )
  },
})
```

## Manual SSR Entry Point (Advanced)

If you need more control or want to provide a manual `setup` callback, create a separate `frontend/ssr.tsx` entry point. Note that using a manual `setup` prevents the Vite plugin from auto-generating SSR handling.

```tsx
import { createInertiaApp } from '@inertiajs/react'
import createServer from '@inertiajs/react/server'
import ReactDOMServer from 'react-dom/server'

createServer(page =>
  createInertiaApp({
    page,
    render: ReactDOMServer.renderToString,
    resolve: name => {
      const pages = import.meta.glob('./pages/**/*.tsx')
      return pages[`./pages/${name}.tsx`]()
    },
    setup: ({ App, props }) => <App {...props} />,
  }),
)
```

You'll also need to update your `app.tsx` to use client-side hydration:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { hydrateRoot } from 'react-dom/client'

createInertiaApp({
  resolve: name => {
    const pages = import.meta.glob('./pages/**/*.tsx')
    return pages[`./pages/${name}.tsx`]()
  },
  setup({ el, App, props }) {
    hydrateRoot(el, <App {...props} />)
  },
})
```

## SSR with Lifespan Management

For production deployments, you'll want to manage the SSR server lifecycle automatically. See the [SSR Lifespan](/docs/ssr-lifespan) guide for details.
