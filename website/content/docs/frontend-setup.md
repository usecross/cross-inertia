---
title: Frontend Setup
description: Set up React with Vite for your Inertia.js + FastAPI application
---

This guide walks you through setting up a React frontend with Vite for your Inertia.js + FastAPI application.

## Prerequisites

- Node.js 18+ (or Bun)
- A FastAPI application with cross-inertia installed

## Project Structure

A typical Inertia.js + FastAPI project looks like this:

```
my-app/
├── frontend/              # React frontend code
│   ├── app.tsx           # Inertia app entry point
│   ├── globals.css       # Global styles
│   ├── components/       # Shared components
│   │   └── Layout.tsx
│   └── pages/            # Page components
│       ├── Home.tsx
│       └── Users/
│           ├── Index.tsx
│           └── Show.tsx
├── templates/
│   └── app.html          # Root HTML template
├── static/               # Static assets (built files go here)
├── main.py               # FastAPI application
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Step 1: Initialize Frontend

Create a `package.json` with the required dependencies:

```json
{
  "name": "my-inertia-app",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@inertiajs/react": "^2.0.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.3",
    "vite": "^5.4.2"
  }
}
```

Install dependencies:

```bash
# Using npm
npm install

# Using bun
bun install

# Using pnpm
pnpm install
```

## Step 2: Configure Vite

Create `vite.config.ts`:

```typescript
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

Key settings:
- **`manifest: true`** - Generates a manifest file for production asset loading
- **`outDir: 'static/build'`** - Where built files are placed
- **`input: 'frontend/app.tsx'`** - Your app's entry point

## Step 3: Configure TypeScript

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./frontend/*"]
    }
  },
  "include": ["frontend"]
}
```

## Step 4: Create the Inertia App Entry Point

Create `frontend/app.tsx`:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'
import './globals.css'

// Option 1: Explicit imports (recommended for smaller apps)
import Home from './pages/Home'
import About from './pages/About'
import UsersIndex from './pages/Users/Index'
import UsersShow from './pages/Users/Show'

const pages: Record<string, React.ComponentType<any>> = {
  Home,
  About,
  'Users/Index': UsersIndex,
  'Users/Show': UsersShow,
}

createInertiaApp({
  resolve: (name) => {
    const page = pages[name]
    if (!page) {
      throw new Error(`Page component "${name}" not found`)
    }
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
```

### Dynamic Imports (Alternative)

For larger apps, use dynamic imports with `import.meta.glob`:

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'
import './globals.css'

createInertiaApp({
  resolve: (name) => {
    const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })
    const page = pages[`./pages/${name}.tsx`]
    if (!page) {
      throw new Error(`Page component "${name}" not found`)
    }
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
```

## Step 5: Create the Root HTML Template

Create `templates/app.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>
```

The `{{ vite() }}` function automatically includes:
- React Fast Refresh scripts (dev mode)
- Vite client scripts (dev mode)
- Built CSS and JS files (production mode)

### Using View Data for SEO

For dynamic page titles and meta tags, use [view data](/guides/view-data/):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if page_title %}{{ page_title }}{% else %}My App{% endif %}</title>
    {% if meta_description %}
    <meta name="description" content="{{ meta_description }}">
    {% endif %}
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>
```

## Step 6: Create Your First Page

Create `frontend/pages/Home.tsx`:

```tsx
import { Link } from '@inertiajs/react'

interface HomeProps {
  message: string
}

export default function Home({ message }: HomeProps) {
  return (
    <div>
      <h1>Welcome</h1>
      <p>{message}</p>
      <Link href="/about">Go to About</Link>
    </div>
  )
}
```

## Step 7: Create a Layout Component

Create `frontend/components/Layout.tsx`:

```tsx
import { Link, usePage } from '@inertiajs/react'
import React from 'react'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

interface SharedProps {
  auth: {
    user: {
      id: number
      name: string
    }
  }
  flash: {
    message?: string
    category?: 'success' | 'error'
  }
}

export default function Layout({ children, title }: LayoutProps) {
  const { auth, flash } = usePage<SharedProps>().props

  return (
    <div className="min-h-screen">
      <nav className="bg-gray-800 text-white p-4">
        <div className="container mx-auto flex justify-between">
          <Link href="/" className="font-bold">My App</Link>
          <div className="flex gap-4">
            <Link href="/">Home</Link>
            <Link href="/about">About</Link>
            <span>{auth.user.name}</span>
          </div>
        </div>
      </nav>

      {flash.message && (
        <div className={`p-4 ${flash.category === 'error' ? 'bg-red-100' : 'bg-green-100'}`}>
          {flash.message}
        </div>
      )}

      <main className="container mx-auto p-4">
        {title && <h1 className="text-2xl font-bold mb-4">{title}</h1>}
        {children}
      </main>
    </div>
  )
}
```

Use the layout in your pages:

```tsx
import Layout from '@/components/Layout'

export default function Home({ message }: HomeProps) {
  return (
    <Layout title="Home">
      <p>{message}</p>
    </Layout>
  )
}
```

## Step 8: Add Global Styles

Create `frontend/globals.css`:

```css
/* Basic reset */
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}

/* Or import Tailwind CSS */
/* @tailwind base;
@tailwind components;
@tailwind utilities; */
```

## Running the Application

### Development Mode

Start both the Vite dev server and FastAPI:

```bash
# Terminal 1: Start Vite
npm run dev

# Terminal 2: Start FastAPI
uvicorn main:app --reload
```

Or create a `run-dev.sh` script:

```bash
#!/bin/bash
# Start Vite in background
npm run dev &
VITE_PID=$!

# Start FastAPI
uvicorn main:app --reload

# Cleanup on exit
trap "kill $VITE_PID" EXIT
```

### Production Build

Build the frontend assets:

```bash
npm run build
```

This creates:
- `static/build/.vite/manifest.json` - Asset manifest
- `static/build/assets/` - Compiled JS and CSS files

Start FastAPI (no Vite needed in production):

```bash
uvicorn main:app
```

## TypeScript Types

### Page Props Types

Define types for your page components:

```tsx
// frontend/types.ts
export interface User {
  id: number
  name: string
  email: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  has_more: boolean
}
```

```tsx
// frontend/pages/Users/Index.tsx
import { User, PaginatedResponse } from '@/types'

interface UsersIndexProps {
  users: PaginatedResponse<User>
}

export default function UsersIndex({ users }: UsersIndexProps) {
  return (
    <div>
      {users.data.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  )
}
```

### Shared Props Types

Type your shared data:

```tsx
// frontend/types.ts
export interface SharedProps {
  auth: {
    user: User | null
  }
  flash: {
    message?: string
    category?: 'success' | 'error' | 'warning' | 'info'
  }
  // Add other shared props
}
```

```tsx
import { usePage } from '@inertiajs/react'
import { SharedProps } from '@/types'

export default function Layout({ children }) {
  const { auth, flash } = usePage<SharedProps>().props
  // ...
}
```

## Common Patterns

### Using Forms

```tsx
import { useForm } from '@inertiajs/react'

export default function ContactForm() {
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    email: '',
    message: '',
  })

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/contact')
  }

  return (
    <form onSubmit={submit}>
      <input
        value={data.name}
        onChange={e => setData('name', e.target.value)}
      />
      {errors.name && <span>{errors.name}</span>}

      <button type="submit" disabled={processing}>
        Send
      </button>
    </form>
  )
}
```

### Navigation with `router`

```tsx
import { router } from '@inertiajs/react'

// Navigate programmatically
router.visit('/users/1')

// With options
router.visit('/users', {
  method: 'get',
  preserveState: true,
  preserveScroll: true,
  only: ['users'],
})

// POST request
router.post('/users', { name: 'John' })

// Reload current page
router.reload()
```

### Progress Indicator

Add a loading indicator for navigation:

```tsx
import { router } from '@inertiajs/react'
import { useEffect, useState } from 'react'

export default function Layout({ children }) {
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const start = () => setLoading(true)
    const finish = () => setLoading(false)

    router.on('start', start)
    router.on('finish', finish)

    return () => {
      router.off('start', start)
      router.off('finish', finish)
    }
  }, [])

  return (
    <div>
      {loading && <div className="progress-bar" />}
      {children}
    </div>
  )
}
```

## Next Steps

- [Configuration](/guides/configuration/) - Customize Inertia settings
- [Shared Data](/guides/shared-data/) - Pass data to all pages
- [Validation Errors](/guides/validation-errors/) - Handle form errors
- [Partial Reloads](/guides/partial-reloads/) - Optimize data loading
