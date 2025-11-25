"""
Inertia.js adapter for Python web frameworks.

This package provides server-side adapters for Inertia.js.

Framework-specific imports:
    from inertia.fastapi import InertiaDep, InertiaMiddleware

Prop types (following Laravel Inertia conventions):
    from inertia import optional, always

    return inertia.render("Page", {
        "user": get_user(),                        # Regular prop
        "permissions": optional(get_permissions),  # Only when explicitly requested
        "flash": always(get_flash),                # Always included, even in partial reloads
    })
"""

from importlib.metadata import version

from inertia._core import optional, always

__version__ = version("cross-inertia")
__all__ = ["optional", "always", "__version__"]
