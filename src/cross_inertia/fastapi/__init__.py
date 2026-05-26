"""
FastAPI-specific Inertia.js adapter exports.

This module contains FastAPI-specific classes, functions, and type aliases
for integrating Inertia.js with FastAPI applications.

Example:
    from cross_inertia.fastapi import (
        InertiaDep,
        inertia_exception_handlers,
        inertia_share,
    )
    from starlette.middleware.sessions import SessionMiddleware

    @inertia_share
    async def share_auth(request: Request):
        return {"auth": {"user": get_user(request)}}

    app = FastAPI(
        dependencies=[Depends(share_auth)],
        exception_handlers=inertia_exception_handlers(),
    )
    app.add_middleware(SessionMiddleware, secret_key="change-me")

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

from typing import Annotated

from cross_web import StarletteRequestAdapter
from fastapi import Depends, Request

from .._core import (
    Inertia,
    InertiaResponse,
    get_inertia_response,
)
from .share import inertia_share
from .validation import (
    inertia_exception_handlers,
    inertia_validation_exception_handler,
    pop_validation_errors_from_session,
    store_current_url_as_previous_url,
)

InertiaResponseDep = Annotated[InertiaResponse, Depends(get_inertia_response)]


def get_inertia(
    request: Request,
    inertia_response: InertiaResponseDep,
) -> Inertia:
    """FastAPI dependency to get a request-scoped Inertia renderer."""

    adapter = StarletteRequestAdapter(request)
    store_current_url_as_previous_url(request)
    return Inertia(
        request,
        adapter,
        inertia_response,
        validation_errors=pop_validation_errors_from_session(request),
    )


InertiaDep = Annotated[Inertia, Depends(get_inertia)]

__all__ = [
    "Inertia",
    "InertiaResponse",
    "InertiaDep",
    "get_inertia",
    "get_inertia_response",
    "inertia_share",
    "inertia_exception_handlers",
    "inertia_validation_exception_handler",
]
