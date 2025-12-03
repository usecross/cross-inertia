---
title: Quick Start
description: Get up and running with Cross-Inertia in minutes.
order: 2
section: Getting Started
---

## Prerequisites

Before you begin, make sure you have:

- Python 3.10 or higher
- Node.js 18+ or Bun
- Basic familiarity with FastAPI and React

## Step 1: Create your project

Create a new directory and set up your Python environment:

```bash
mkdir my-inertia-app
cd my-inertia-app
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Step 2: Install dependencies

Install Cross-Inertia and FastAPI:

```bash
pip install cross-inertia fastapi uvicorn jinja2
```

Install the frontend dependencies:

```bash
bun init -y
bun add react react-dom @inertiajs/react
bun add -d vite @vitejs/plugin-react typescript @types/react @types/react-dom
```

## Step 3: Create your FastAPI app

Create a `main.py` file:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaDep

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello from Cross-Inertia!"
    })
```

## Step 4: Create your template

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

## Step 5: Create your React app

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

## Step 6: Create your first page

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

## Step 7: Run your app

Start both the Vite dev server and FastAPI:

```bash
# Terminal 1: Start Vite
bun run vite

# Terminal 2: Start FastAPI
uvicorn main:app --reload
```

Visit `http://localhost:8000` to see your app!
