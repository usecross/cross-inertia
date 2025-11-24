"""
Inertia.js adapter for Python web frameworks.

This package provides server-side adapters for Inertia.js.

Framework-specific imports:
    from inertia.fastapi import InertiaDep, InertiaMiddleware

Lazy props:
    from inertia import lazy

    return inertia.render("Page", {
        "user": get_user(),                    # Always included
        "permissions": lazy(get_permissions),  # Only when requested
    })
"""

from importlib.metadata import version

from inertia._core import lazy, LazyProp

__version__ = version("cross-inertia")
__all__ = ["lazy", "LazyProp", "__version__"]
