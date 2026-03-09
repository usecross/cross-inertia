---
title: Installation
description: Install Cross-Inertia and set up your project.
order: 4
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

Cross-Inertia uses [Inertia.js v3](https://inertiajs.com) (currently in beta), which requires Node.js 24+.

Install the Inertia.js client adapter and Vite plugin for your framework of choice:

### React

```bash
bun add @inertiajs/react@beta react react-dom
bun add -d @inertiajs/vite@beta
```

### Vue

```bash
bun add @inertiajs/vue3@beta vue
bun add -d @inertiajs/vite@beta
```

### Svelte

```bash
bun add @inertiajs/svelte@beta svelte
bun add -d @inertiajs/vite@beta
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
    'cross_inertia.django',
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

> **Note:** The `@inertiajs/vite` plugin (installed above) simplifies your setup by automatically handling page component resolution and SSR configuration.

## Verification

You can verify your installation by importing Cross-Inertia:

### FastAPI

```python
from cross_inertia.fastapi import InertiaDep, inertia_share

print("Cross-Inertia installed successfully!")
```

### Django

```python
from cross_inertia.django import render, InertiaMiddleware

print("Cross-Inertia installed successfully!")
```
