"""
Inertia.js adapter for Python web frameworks.

This package provides server-side adapters for Inertia.js.

Framework-specific imports:
    from cross_inertia.fastapi import InertiaDep, inertia_share

Configuration (single source of truth):
    from cross_inertia import configure_inertia
    from cross_inertia.fastapi.experimental import inertia_lifespan

    configure_inertia(
        vite_port="auto",  # Finds an available port automatically
        vite_entry="frontend/app.tsx",
        ssr_enabled=True,
    )

    app = FastAPI(lifespan=inertia_lifespan)

Prop types (following Laravel Inertia conventions):
    from cross_inertia import optional, always, defer, once, live, broadcast_props

    return inertia.render("Page", {
        "user": get_user(),                        # Regular prop
        "permissions": optional(get_permissions),  # Only when explicitly requested
        "flash": always(get_flash),                # Always included, even in partial reloads
        "analytics": defer(get_analytics),         # Loaded after initial render
        "plans": once(load_plans),                 # Remembered across navigations
        "order": live(get_order, on="order.updated", channel={"name": "orders.1", "type": "private"}),  # Auto-refreshes on broadcast
    })
"""

from importlib.metadata import version

from cross_inertia._config import InertiaConfig, configure_inertia, get_config
from cross_inertia._exceptions import InertiaSchemaError, ManifestNotFoundError
from cross_inertia._props import always, broadcast_props, defer, live, once, optional
from cross_inertia._types import ValidationErrors, ValidationErrorValue

__version__ = version("cross-inertia")
__all__ = [
    "InertiaConfig",
    "InertiaSchemaError",
    "ManifestNotFoundError",
    "ValidationErrorValue",
    "ValidationErrors",
    "__version__",
    "always",
    "broadcast_props",
    "configure_inertia",
    "defer",
    "get_config",
    "live",
    "once",
    "optional",
]
