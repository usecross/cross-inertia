---
title: Installation
description: Install Cross-Inertia and set up your project.
order: 3
section: Getting Started
---

## Server-side installation

Install Cross-Inertia using pip:

```bash
pip install cross-inertia
```

Or with uv:

```bash
uv add cross-inertia
```

## Client-side installation

Install the Inertia.js client adapter for your framework of choice:

### React

```bash
bun add @inertiajs/react react react-dom
```

### Vue

```bash
bun add @inertiajs/vue3 vue
```

### Svelte

```bash
bun add @inertiajs/svelte svelte
```

## Additional dependencies

You'll also need Jinja2 for templating:

```bash
pip install jinja2
```

And for server-side rendering support:

```bash
pip install httpx
```

## Build tools

We recommend using Vite for building your frontend assets:

```bash
bun add -d vite @vitejs/plugin-react typescript
```

## Verification

You can verify your installation by importing Cross-Inertia:

```python
from inertia.fastapi import InertiaDep, InertiaMiddleware, InertiaResponse

print("Cross-Inertia installed successfully!")
```
