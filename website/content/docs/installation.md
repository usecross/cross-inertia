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

## Framework-specific dependencies

### FastAPI

For FastAPI, you'll need Jinja2 for templating:

```bash
pip install jinja2
```

### Django

Django works out of the box with its built-in template engine. Just add to your installed apps:

```python
INSTALLED_APPS = [
    # ...
    'inertia.django',
]
```

## SSR support

For server-side rendering support (both frameworks):

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

### FastAPI

```python
from inertia.fastapi import InertiaDep, InertiaMiddleware

print("Cross-Inertia installed successfully!")
```

### Django

```python
from inertia.django import render, InertiaMiddleware

print("Cross-Inertia installed successfully!")
```
