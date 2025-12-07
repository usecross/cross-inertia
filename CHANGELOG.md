

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
