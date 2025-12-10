---
title: Quick Start
description: Get up and running with Cross-Inertia in minutes.
order: 2
section: Getting Started
---

## Prerequisites

Before you begin, make sure you have:

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 18+ or Bun
- Basic familiarity with FastAPI and React

## Step 1: Create your project

Create a new directory and set up your Python environment with uv:

```bash
mkdir my-inertia-app
cd my-inertia-app
uv init
```

## Step 2: Install Python dependencies

Install Cross-Inertia and FastAPI:

```bash
uv add cross-inertia "fastapi[standard]" jinja2
```

> **Note:** `fastapi[standard]` includes uvicorn, so you don't need to install it separately.

## Step 3: Install frontend dependencies

Initialize your frontend and install the required packages:

```bash
bun init -y
bun add react react-dom @inertiajs/react
bun add -d vite @vitejs/plugin-react typescript @types/react @types/react-dom @types/node
```

## Step 4: Configure Vite

Create a `vite.config.ts` file:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend'),
    },
  },
  build: {
    manifest: true,
    outDir: 'static/build',
    rollupOptions: {
      input: 'frontend/app.tsx',
    },
  },
  server: {
    port: 5173,
    strictPort: true,
  },
})
```

Add scripts to your `package.json`:

```json
{
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build"
  }
}
```

## Step 5: Create your FastAPI app

Create a `main.py` file with the experimental lifespan for automatic Vite dev server management:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaDep
from inertia.fastapi.experimental import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello from Cross-Inertia!"
    })
```

> **Note:** The `inertia_lifespan` automatically starts the Vite dev server when running `fastapi dev`. See [Experimental Lifespan](/docs/experimental-lifespan) for configuration options.

## Step 6: Create your template

Create a `templates/app.html` file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Inertia App</title>
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>
```

## Step 7: Create your React app

Create a `frontend/app.tsx` file:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })

createInertiaApp({
  resolve: (name) => {
    const page = pages[`./pages/${name}.tsx`]
    if (!page) throw new Error(`Page ${name} not found`)
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
```

## Step 8: Create your first page

Create a `frontend/pages/Home.tsx` file:

```tsx
interface HomeProps {
  message: string
}

export default function Home({ message }: HomeProps) {
  return (
    <div>
      <h1>{message}</h1>
      <p>Welcome to your Inertia app!</p>
    </div>
  )
}
```

## Step 9: Create required directories

```bash
mkdir -p static templates frontend/pages
```

## Step 10: Run your app

Start FastAPI in development mode - Vite will start automatically:

```bash
fastapi dev main.py
```

Visit `http://localhost:8000` to see your app!

## Manual Vite Setup (Alternative)

If you prefer to manage the Vite dev server manually instead of using `inertia_lifespan`:

```bash
# Terminal 1: Start Vite
bun run dev

# Terminal 2: Start FastAPI
fastapi dev main.py
```

## Next Steps

- Learn about [Pages](/docs/pages) and how to pass props
- Set up [Shared Data](/docs/shared-data) for global state
- Configure [SSR](/docs/ssr) for production
