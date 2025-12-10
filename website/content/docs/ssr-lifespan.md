---
title: SSR Lifespan
description: Manage the SSR server lifecycle with your FastAPI application.
order: 9
section: Advanced
---

## Overview

Cross-Inertia provides a `ssr_lifespan` context manager that automatically starts and stops the SSR server alongside your FastAPI application. This ensures the SSR server is always available when your app is running.

## Basic Usage

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.ssr import ssr_lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with ssr_lifespan(
        command=["bun", "run", "static/build/ssr/ssr.js"],
        ssr_url="http://localhost:13714",
    ):
        yield

app = FastAPI(lifespan=lifespan)
```

## Configuration Options

The `ssr_lifespan` function accepts these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | `list[str]` | The command to start the SSR server |
| `ssr_url` | `str` | URL where the SSR server will listen |
| `timeout` | `float` | Seconds to wait for server startup (default: 10.0) |
| `health_check_interval` | `float` | Seconds between health checks (default: 0.5) |

## Combining with Other Lifespans

You can combine `ssr_lifespan` with other lifespan managers:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.ssr import ssr_lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()

    async with ssr_lifespan(
        command=["bun", "run", "static/build/ssr/ssr.js"],
        ssr_url="http://localhost:13714",
    ):
        yield

    # Cleanup
    await close_db()

app = FastAPI(lifespan=lifespan)
```

## Development vs Production

In development, you typically don't need SSR since Vite handles hot module replacement. Use conditional logic:

```python
import sys

DEBUG = "dev" in sys.argv

@asynccontextmanager
async def lifespan(app: FastAPI):
    if DEBUG:
        # No SSR in development
        yield
    else:
        async with ssr_lifespan(
            command=["bun", "run", "static/build/ssr/ssr.js"],
            ssr_url="http://localhost:13714",
        ):
            yield

app = FastAPI(lifespan=lifespan)
```

## Error Handling

The `ssr_lifespan` manager handles common errors gracefully:

- **Startup timeout**: Raises an exception if the SSR server doesn't respond within the timeout period
- **Process crash**: Logs an error and allows the app to continue without SSR
- **Graceful shutdown**: Sends SIGTERM to the SSR process and waits for clean exit
