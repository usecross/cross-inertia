"""
Inertia.js adapter for Python web frameworks.

This package provides server-side adapters for Inertia.js.

DEPRECATED: Top-level imports are deprecated and will be removed in v1.0.0.
Please use framework-specific imports instead:

    # New (recommended)
    from inertia.fastapi import InertiaDep, InertiaMiddleware

    # Old (deprecated)
    from inertia import InertiaDep, InertiaMiddleware

See https://github.com/patrick91/cross-inertia/issues/10 for details.
"""

import warnings

# Framework-specific exports are now in submodules
# Import them here for backward compatibility with deprecation warnings


def __getattr__(name: str):
    """
    Provide backward compatibility for old imports with deprecation warnings.

    This allows `from inertia import InertiaDep` to still work, but with a warning.
    """
    # List of FastAPI-specific exports that should be imported from inertia.fastapi
    fastapi_exports = {
        "Inertia",
        "InertiaDep",
        "InertiaResponse",
        "InertiaMiddleware",
        "get_inertia",
        "get_inertia_response",
        "read_vite_entry_from_config",
    }

    if name in fastapi_exports:
        warnings.warn(
            f"Importing '{name}' from 'inertia' is deprecated and will be removed in v1.0.0. "
            f"Please use 'from inertia.fastapi import {name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import and return the attribute from the fastapi module
        from . import fastapi

        return getattr(fastapi, name)

    raise AttributeError(f"module 'inertia' has no attribute '{name}'")


def __dir__():
    """List available attributes for autocomplete."""
    return [
        "__version__",
        # Include deprecated exports for backward compatibility
        "Inertia",
        "InertiaDep",
        "InertiaResponse",
        "InertiaMiddleware",
        "get_inertia",
        "get_inertia_response",
        "read_vite_entry_from_config",
    ]


__version__ = "0.1.0"
