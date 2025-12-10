"""
Inertia.js adapter for Python web frameworks.

This package provides server-side adapters for Inertia.js.

Framework-specific imports:
    from inertia.fastapi import InertiaDep, InertiaMiddleware

Configuration (single source of truth):
    from inertia import configure_inertia
    from inertia.fastapi.experimental import inertia_lifespan

    configure_inertia(
        vite_port="auto",  # Finds an available port automatically
        vite_entry="frontend/app.tsx",
        ssr_enabled=True,
    )

    app = FastAPI(lifespan=inertia_lifespan)

Prop types (following Laravel Inertia conventions):
    from inertia import optional, always, defer

    return inertia.render("Page", {
        "user": get_user(),                        # Regular prop
        "permissions": optional(get_permissions),  # Only when explicitly requested
        "flash": always(get_flash),                # Always included, even in partial reloads
        "analytics": defer(get_analytics),         # Loaded after initial render
    })
"""

from importlib.metadata import version

from inertia._core import optional, always, defer, ManifestNotFoundError
from inertia._config import configure_inertia, get_config, InertiaConfig

__version__ = version("cross-inertia")
__all__ = [
    "optional",
    "always",
    "defer",
    "configure_inertia",
    "get_config",
    "InertiaConfig",
    "ManifestNotFoundError",
    "__version__",
]
