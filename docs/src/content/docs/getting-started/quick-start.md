---
title: Quick Start
description: Build your first app with Cross-Inertia
---

This guide will walk you through creating a simple Inertia.js app with FastAPI and React.

## 1. Create FastAPI App

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello from Inertia!"
    })
```

## 2. Create Template

Create `templates/app.html`:

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

## 3. Create React Component

Create `frontend/app.tsx`:

```typescript
import { createRoot } from 'react-dom/client'
import { createInertiaApp } from '@inertiajs/react'

createInertiaApp({
  resolve: (name) => {
    const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })
    return pages[`./pages/${name}.tsx`]
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
```

Create `frontend/pages/Home.tsx`:

```typescript
export default function Home({ message }: { message: string }) {
  return (
    <div>
      <h1>{message}</h1>
      <p>Welcome to Inertia.js with FastAPI!</p>
    </div>
  )
}
```

## 4. Run Development Server

Terminal 1 - Start Vite:
```bash
npm run dev
# or
bun run dev
```

Terminal 2 - Start FastAPI:
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` and you should see your app!

## Next Steps

- [Configuration](/guides/configuration/) - Customize your setup
- [Validation Errors](/guides/validation-errors/) - Handle form validation
- [Partial Reloads](/guides/partial-reloads/) - Optimize data loading
