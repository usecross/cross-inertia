"""Experimental FastAPI features for Cross-Inertia.

.. warning::
    All modules in this package are experimental and may change in future versions.
    Use with caution in production environments.

SSR lifespan management:
    from inertia.fastapi.experimental import inertia_lifespan, create_ssr_lifespan

    # Simple usage
    app = FastAPI(lifespan=inertia_lifespan)

    # Composable approach
    @asynccontextmanager
    async def lifespan(app):
        async with create_ssr_lifespan():
            yield

    app = FastAPI(lifespan=lifespan)
"""

from .lifespan import (
    inertia_lifespan,
    create_ssr_lifespan,
    SSRServer,
    SSRServerError,
)

__all__ = [
    "inertia_lifespan",
    "create_ssr_lifespan",
    "SSRServer",
    "SSRServerError",
]
