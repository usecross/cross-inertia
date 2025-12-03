---
title: SSR Server Lifespan
description: Automatically manage your SSR server with FastAPI's lifespan
---

Cross-Inertia provides utilities to automatically start and stop your SSR server alongside your FastAPI application. This eliminates the need to manually manage the SSR subprocess.

## Quick Start

The simplest way to use lifespan management is with `inertia_lifespan`:

```python
from fastapi import FastAPI
from inertia import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
```

This will:
- Start the SSR server when your FastAPI app starts
- Stop the SSR server when your FastAPI app shuts down
- Wait for the SSR server to become healthy before accepting requests

## Configuration via Environment Variables

When using `inertia_lifespan`, you can configure the SSR server via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `INERTIA_SSR_COMMAND` | `bun dist/ssr/ssr.js` | Command to start the SSR server |
| `INERTIA_SSR_CWD` | Current directory | Working directory for the SSR server |
| `INERTIA_SSR_HEALTH_URL` | `http://127.0.0.1:13714/health` | Health check endpoint |
| `INERTIA_SSR_TIMEOUT` | `10` | Startup timeout in seconds |

Example with environment variables:

```bash
INERTIA_SSR_COMMAND="node dist/ssr/server.js" uvicorn main:app
```

## Composable Approach

For more control, use `create_ssr_lifespan` which can be composed with other lifespan managers:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app):
    # Your startup logic here
    print("Starting up...")

    async with create_ssr_lifespan(
        command="bun dist/ssr/ssr.js",
        startup_timeout=15.0,
    ):
        yield

    # Your shutdown logic here
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

### Configuration Options

`create_ssr_lifespan` accepts these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `str \| list[str]` | `"bun dist/ssr/ssr.js"` | SSR server command |
| `cwd` | `str \| None` | `None` | Working directory |
| `health_url` | `str` | `http://127.0.0.1:13714/health` | Health check URL |
| `startup_timeout` | `float` | `10.0` | Seconds to wait for health |
| `env` | `dict[str, str] \| None` | `None` | Additional environment variables |

### Using List Commands

You can also pass the command as a list for more precise control:

```python
async with create_ssr_lifespan(
    command=["node", "server.js", "--port", "13714"],
    cwd="/path/to/ssr",
):
    yield
```

### Accessing the Server Instance

The context manager yields an `SSRServer` instance that you can use to check status:

```python
@asynccontextmanager
async def lifespan(app):
    async with create_ssr_lifespan() as ssr_server:
        print(f"SSR server running: {ssr_server.is_running}")
        yield
```

## Error Handling

If the SSR server fails to start or become healthy within the timeout, an `SSRServerError` is raised:

```python
from inertia import create_ssr_lifespan, SSRServerError

@asynccontextmanager
async def lifespan(app):
    try:
        async with create_ssr_lifespan():
            yield
    except SSRServerError as e:
        print(f"SSR server failed to start: {e}")
        # You might want to continue without SSR
        yield
```

## Complete Example

Here's a complete example with SSR, custom configuration, and other lifespan operations:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaDep, InertiaMiddleware, create_ssr_lifespan

@asynccontextmanager
async def lifespan(app):
    # Connect to database, etc.
    print("Connecting to database...")

    # Start SSR server
    async with create_ssr_lifespan(
        command="bun dist/ssr/ssr.js",
        startup_timeout=15.0,
        env={"NODE_ENV": "production"},
    ):
        yield

    # Cleanup
    print("Closing database connection...")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

def share_data(request):
    return {"app_name": "My App"}

app.add_middleware(InertiaMiddleware, share=share_data)

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {"message": "Hello!"})
```

## SSR Server Requirements

Your SSR server must implement these endpoints:

- `GET /health` - Returns 200 when the server is ready
- `POST /render` - Accepts Inertia page data and returns `{head: [...], body: "..."}`

See the [Inertia.js SSR documentation](https://inertiajs.com/server-side-rendering) for more details on implementing an SSR server.

## Next Steps

- [Configuration](/guides/configuration/) - Configure InertiaResponse with SSR enabled
- [View Data](/guides/view-data/) - Pass data to your templates for SSR
