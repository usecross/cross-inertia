
0.11.0 - 2025-12-07
-------------------

Add Vite dev server support to lifespan management

The `inertia_lifespan` now auto-detects development mode and starts the appropriate servers:

- **Dev mode** (`fastapi dev`): Starts Vite dev server for HMR
- **Production** (`fastapi run`): Starts SSR server

```python
from fastapi import FastAPI
from inertia.fastapi.experimental import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
```

New exports:
- `ViteDevServer`: Class to manage Vite subprocess
- `ViteServerError`: Exception for Vite server failures
- `create_vite_lifespan()`: Composable context manager for Vite
- `is_dev_mode()`: Helper to detect development mode

Environment variables for configuration:
- `INERTIA_DEV`: Force dev mode on/off
- `INERTIA_VITE_COMMAND`: Vite start command (default: `bun run dev`)
- `INERTIA_SSR_ENABLED`: Enable/disable SSR in production

0.10.1 - 2025-12-07
-------------------

Make `share` parameter optional in `InertiaMiddleware`

The `share` parameter now defaults to `None`, allowing simpler middleware setup when shared data is not needed:

```python
# Before (required)
app.add_middleware(InertiaMiddleware, share=lambda request: {})

# After (optional)
app.add_middleware(InertiaMiddleware)
```

0.10.0 - 2025-12-03
-------------------

Add experimental lifespan SSR server management

Auto-start/stop the SSR server with FastAPI's lifespan context manager, so users don't need to manage the SSR subprocess manually.

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

0.9.0 - 2025-12-03
------------------

Add Server-Side Rendering (SSR) support

Enable SSR by passing `ssr_enabled=True` to `InertiaResponse`:

```python
inertia_response = InertiaResponse(
    ssr_enabled=True,
    ssr_url="http://localhost:13714",  # optional, this is the default
)
```

- Add `ssr_enabled` and `ssr_url` parameters to `InertiaResponse`
- SSR server must implement the Inertia SSR protocol (`POST /render`, `GET /health`)
- Graceful fallback to client-side rendering (CSR) when SSR fails or times out
- Template context now includes `ssr_head` and `ssr_body` variables for SSR output

0.8.0 - 2025-11-25
------------------

Add X-Inertia-Reset header support for infinite scroll reset

- Handle X-Inertia-Reset header to clear props before merging
- Filter reset props from mergeProps, prependProps, deepMergeProps
- Support nested prop paths (e.g., reset "cats" excludes "cats.data")
- Include resetProps in response for client-side handling
- Fix URL handling to include query strings in responses
