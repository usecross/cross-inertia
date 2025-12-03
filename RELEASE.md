---
release type: minor
---

Add lifespan SSR server management

Auto-start/stop the SSR server with FastAPI's lifespan context manager,
so users don't need to manage the SSR subprocess manually.

Simple usage:

```python
from fastapi import FastAPI
from inertia import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
```

Composable approach:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app):
    async with create_ssr_lifespan(command="bun dist/ssr/ssr.js"):
        yield

app = FastAPI(lifespan=lifespan)
```

- Add `inertia_lifespan` for simple usage with environment variable config
- Add `create_ssr_lifespan` for composable approach with full control
- Add `SSRServer` class and `SSRServerError` exception
