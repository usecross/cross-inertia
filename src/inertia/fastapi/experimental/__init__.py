"""Experimental FastAPI features for Cross-Inertia.

.. warning::
    All modules in this package are experimental and may change in future versions.
    Use with caution in production environments.

SSR and Vite lifespan management:
    from inertia.fastapi.experimental import inertia_lifespan, create_ssr_lifespan

    # Simple usage - auto-detects dev mode (fastapi dev) and starts Vite/SSR accordingly
    app = FastAPI(lifespan=inertia_lifespan)

    # Composable approach
    @asynccontextmanager
    async def lifespan(app):
        async with create_ssr_lifespan():
            async with create_vite_lifespan():
                yield

    app = FastAPI(lifespan=lifespan)
"""

from .lifespan import (
    inertia_lifespan,
    create_ssr_lifespan,
    create_vite_lifespan,
    is_dev_mode,
    SSRServer,
    SSRServerError,
    ViteDevServer,
    ViteServerError,
)

__all__ = [
    "inertia_lifespan",
    "create_ssr_lifespan",
    "create_vite_lifespan",
    "is_dev_mode",
    "SSRServer",
    "SSRServerError",
    "ViteDevServer",
    "ViteServerError",
]
