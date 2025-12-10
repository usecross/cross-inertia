---
title: Introduction
description: Cross-Inertia is an Inertia.js adapter for Python backends, letting you build modern single-page apps using classic server-side routing.
order: 1
section: Getting Started
---

## What is Cross-Inertia?

Cross-Inertia is an Inertia.js adapter for Python backends. It allows you to build modern single-page applications using classic server-side routing and controllers.

Instead of building an API and a separate SPA frontend, you can build a monolithic application where your Python backend renders React, Vue, or Svelte components directly.

## How it works

Inertia sits between your server-side framework and your client-side framework. On the initial page visit, Inertia returns a full HTML document. Subsequent visits return JSON responses that update the page without a full reload.

```python
# Your FastAPI route returns a component name and props
@app.get("/users/{id}")
async def show_user(id: int, inertia: InertiaDep):
    user = await get_user(id)
    return inertia.render("Users/Show", {"user": user})
```

The client-side adapter receives this data and renders the appropriate component with the provided props.

## Why use Inertia?

- **No API needed** - Skip building a separate REST or GraphQL API. Your controllers return page components directly.
- **Server-side routing** - Use your familiar Python routing. No client-side router needed.
- **Full SPA experience** - Users get the speed and responsiveness of a single-page app without the complexity.
- **SEO friendly** - With server-side rendering support, your pages are fully indexable by search engines.

## Next steps

Ready to get started? Check out the [Quick Start guide](/docs/quick-start) to build your first Cross-Inertia application.
