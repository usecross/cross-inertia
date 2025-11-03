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
"""

from ._core import (
    Inertia,
    InertiaDep,
    InertiaResponse,
    get_inertia,
    get_inertia_response,
    read_vite_entry_from_config,
)
from .middleware import InertiaMiddleware

__all__ = [
    "Inertia",
    "InertiaResponse",
    "InertiaMiddleware",
    "InertiaDep",
    "get_inertia",
    "get_inertia_response",
    "read_vite_entry_from_config",
]
