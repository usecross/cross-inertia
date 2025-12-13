"""
FastAPI-specific Inertia.js adapter exports.

This module contains FastAPI-specific classes, functions, and type aliases
for integrating Inertia.js with FastAPI applications.

Example:
    from inertia.fastapi import InertiaDep, InertiaMiddleware

    app = FastAPI()
    app.add_middleware(InertiaMiddleware, share=share_data)

    @app.get("/")
    async def home(inertia: InertiaDep):
        return inertia.render("Home", {"message": "Hello World"})

Experimental SSR lifespan management:
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

from .._core import (
    Inertia,
    InertiaDep,
    InertiaResponse,
    get_inertia,
    get_inertia_response,
)
from ..middleware import InertiaMiddleware

__all__ = [
    "Inertia",
    "InertiaResponse",
    "InertiaMiddleware",
    "InertiaDep",
    "get_inertia",
    "get_inertia_response",
]
