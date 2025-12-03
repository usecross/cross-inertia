

0.10.0 - 2025-12-03
-------------------

Add experimental lifespan SSR server management

Auto-start/stop the SSR server with FastAPI's lifespan context manager,
so users don't need to manage the SSR subprocess manually.

This feature is marked as experimental and available under `inertia.fastapi.experimental`.

Simple usage:

```python
from fastapi import FastAPI
from inertia.fastapi.experimental import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
```

Composable approach:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app):
    async with create_ssr_lifespan(command="bun dist/ssr/ssr.js"):
        yield

app = FastAPI(lifespan=lifespan)
```

- Add `inertia_lifespan` for simple usage with environment variable config
- Add `create_ssr_lifespan` for composable approach with full control
- Add `SSRServer` class and `SSRServerError` exception
