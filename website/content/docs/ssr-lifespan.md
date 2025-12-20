---
title: SSR Lifespan
description: Manage the SSR server lifecycle with your FastAPI application.
order: 9
section: Advanced
---

:::note
For more comprehensive documentation and examples, see the [Experimental Lifespan](./experimental-lifespan.md) page.
:::

## Overview

Cross-Inertia provides a `create_ssr_lifespan` context manager that automatically starts and stops the SSR server alongside your FastAPI application. This ensures the SSR server is always available when your app is running.

## Basic Usage

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with create_ssr_lifespan(
        command="bun dist/ssr/ssr.js",
        health_url="http://127.0.0.1:13714/health",
    ):
        yield

app = FastAPI(lifespan=lifespan)
```

## Configuration Options

The `create_ssr_lifespan` function accepts these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | `str \| list[str]` | The command to start the SSR server (default: "bun dist/ssr/ssr.js") |
| `cwd` | `str \| None` | Working directory for the SSR server (default: None) |
| `health_url` | `str` | URL to check for server health (default: "http://127.0.0.1:13714/health") |
| `startup_timeout` | `float` | Maximum time to wait for server startup in seconds (default: 10.0) |
| `env` | `dict[str, str] \| None` | Additional environment variables for the subprocess (default: None) |

## Combining with Other Lifespans

You can combine `create_ssr_lifespan` with other lifespan managers:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()

    async with create_ssr_lifespan(
        command="bun dist/ssr/ssr.js",
        health_url="http://127.0.0.1:13714/health",
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
        async with create_ssr_lifespan(
            command="bun dist/ssr/ssr.js",
            health_url="http://127.0.0.1:13714/health",
        ):
            yield

app = FastAPI(lifespan=lifespan)
```

## Error Handling

The `create_ssr_lifespan` manager handles common errors gracefully:

- **Startup timeout**: Raises `SSRServerError` if the SSR server doesn't respond within the timeout period
- **Process crash**: Raises `SSRServerError` if the process exits unexpectedly during startup
- **Graceful shutdown**: Sends SIGTERM to the SSR process and waits for clean exit (with 5s timeout before force kill)
