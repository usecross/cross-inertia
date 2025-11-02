---
title: Installation
description: How to install Cross-Inertia in your project
---

## Prerequisites

- Python 3.10 or higher
- FastAPI (other frameworks coming soon)
- Node.js or Bun (for frontend build tools)

## Install Cross-Inertia

Currently, Cross-Inertia is not yet published to PyPI. Install from source:

```bash
pip install git+https://github.com/patrick91/cross-inertia.git
```

Or for development:

```bash
git clone https://github.com/patrick91/cross-inertia.git
cd cross-inertia
pip install -e .
```

## Install Frontend Dependencies

Cross-Inertia works with any modern JavaScript framework. Here's an example with React and Vite:

```bash
# Using npm
npm install @inertiajs/react react react-dom

# Or using bun
bun add @inertiajs/react react react-dom
```

## Set Up Vite

Create a `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: 'frontend/app.tsx', // Your entry point
    },
  },
})
```

## Next Steps

- [Quick Start Guide](/getting-started/quick-start/) - Build your first Inertia app
- [Configuration](/guides/configuration/) - Customize the adapter settings
