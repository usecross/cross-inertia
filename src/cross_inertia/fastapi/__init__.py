"""
FastAPI-specific Inertia.js adapter exports.

This module contains FastAPI-specific classes, functions, and type aliases
for integrating Inertia.js with FastAPI applications.

Example:
    from cross_inertia.fastapi import InertiaDep, inertia_share

    @inertia_share
    async def share_auth(request: Request):
        return {"auth": {"user": get_user(request)}}

    app = FastAPI(dependencies=[Depends(share_auth)])

    @app.get("/")
    async def home(inertia: InertiaDep):
        return inertia.render("Home", {"message": "Hello World"})

Experimental SSR lifespan management:
    from cross_inertia.fastapi.experimental import inertia_lifespan, create_ssr_lifespan

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
from .share import inertia_share

__all__ = [
    "Inertia",
    "InertiaResponse",
    "InertiaDep",
    "get_inertia",
    "get_inertia_response",
    "inertia_share",
]
