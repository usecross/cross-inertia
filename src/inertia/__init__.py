"""
Inertia.js adapter for FastAPI.

This package provides a server-side adapter for Inertia.js when using FastAPI.
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

__version__ = "0.1.0"
