---
title: Experimental Lifespan Management
description: Automatic SSR and Vite dev server lifecycle management for FastAPI.
order: 10
section: Advanced
---

> **Warning:** These features are experimental and may change in future versions.

## Overview

Cross-Inertia provides experimental lifespan utilities that automatically manage the SSR server and Vite dev server alongside your FastAPI application. These utilities detect whether you're running in development or production mode and start the appropriate servers.

## Simple Usage

The easiest way to get started is with `inertia_lifespan`:

```python
from fastapi import FastAPI
from inertia.fastapi.experimental import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)
```

This automatically:
- **In development** (`fastapi dev`): Starts the Vite dev server for HMR
- **In production**: Starts the SSR server

## Development Mode Detection

The `is_dev_mode()` function determines the current mode:

```python
from inertia.fastapi.experimental import is_dev_mode

if is_dev_mode():
    print("Running in development mode")
```

Development mode is detected when:
- `INERTIA_DEV` environment variable is `"1"` or `"true"`
- `"dev"` is in `sys.argv` (e.g., `fastapi dev main.py`)

You can force production mode by setting `INERTIA_DEV=0`.

## Composable Approach

For more control, use the individual lifespan managers:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan, create_vite_lifespan

@asynccontextmanager
async def lifespan(app):
    async with create_ssr_lifespan(command="bun dist/ssr/ssr.js"):
        async with create_vite_lifespan():
            # Your other startup logic here
            yield
            # Your other shutdown logic here

app = FastAPI(lifespan=lifespan)
```

### SSR Lifespan Options

```python
async with create_ssr_lifespan(
    command="bun dist/ssr/ssr.js",  # Command to start SSR server
    cwd=None,                        # Working directory
    health_url="http://127.0.0.1:13714/health",  # Health check URL
    startup_timeout=10.0,            # Max wait time in seconds
    env=None,                        # Additional environment variables
) as ssr_server:
    print(f"SSR running: {ssr_server.is_running}")
    yield
```

### Vite Lifespan Options

```python
async with create_vite_lifespan(
    command="bun run dev",           # Command to start Vite
    cwd=None,                        # Working directory
    health_url="http://localhost:5173",  # Vite dev server URL
    startup_timeout=30.0,            # Max wait time in seconds
    env=None,                        # Additional environment variables
) as vite_server:
    print(f"Vite running: {vite_server.is_running}")
    yield
```

## Environment Variables

When using `inertia_lifespan`, you can configure behavior via environment variables:

### Development (Vite)

| Variable | Default | Description |
|----------|---------|-------------|
| `INERTIA_DEV` | auto | Set to `"1"`/`"true"` to force dev mode |
| `INERTIA_VITE_COMMAND` | `"bun run dev"` | Command to start Vite |
| `INERTIA_VITE_CWD` | current dir | Working directory for Vite |
| `INERTIA_VITE_URL` | `"http://localhost:5173"` | Vite dev server URL |
| `INERTIA_VITE_TIMEOUT` | `30` | Startup timeout in seconds |

### Production (SSR)

| Variable | Default | Description |
|----------|---------|-------------|
| `INERTIA_SSR_ENABLED` | `true` | Set to `"0"`/`"false"` to disable SSR |
| `INERTIA_SSR_COMMAND` | `"bun dist/ssr/ssr.js"` | Command to start SSR server |
| `INERTIA_SSR_CWD` | current dir | Working directory for SSR |
| `INERTIA_SSR_HEALTH_URL` | `"http://127.0.0.1:13714/health"` | Health check URL |
| `INERTIA_SSR_TIMEOUT` | `10` | Startup timeout in seconds |

## Error Handling

Both servers raise specific exceptions on failure:

```python
from inertia.fastapi.experimental import SSRServerError, ViteServerError

try:
    async with create_ssr_lifespan():
        yield
except SSRServerError as e:
    print(f"SSR server failed: {e}")
```

Common error scenarios:
- **Command not found**: Raised immediately if the command doesn't exist
- **Startup timeout**: Raised if the server doesn't become healthy in time
- **Process crash**: Raised if the server exits unexpectedly during startup

## Combining with Other Lifespans

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan, is_dev_mode

@asynccontextmanager
async def lifespan(app):
    # Initialize your resources
    await init_database()

    if is_dev_mode():
        # No SSR needed in dev mode
        yield
    else:
        async with create_ssr_lifespan():
            yield

    # Cleanup
    await close_database()

app = FastAPI(lifespan=lifespan)
```

## Direct Server Access

For advanced use cases, you can use the server classes directly:

```python
from inertia.fastapi.experimental import SSRServer, ViteDevServer

# Manual SSR server management
ssr = SSRServer(command="bun dist/ssr/ssr.js")
await ssr.start()
print(f"Running: {ssr.is_running}")
await ssr.stop()

# Manual Vite server management
vite = ViteDevServer(command="bun run dev")
await vite.start()
print(f"Running: {vite.is_running}")
await vite.stop()
```
