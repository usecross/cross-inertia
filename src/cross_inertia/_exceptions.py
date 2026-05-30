"""Inertia exceptions."""


class ManifestNotFoundError(Exception):
    """Raised when the Vite manifest file is not found in production mode."""

    pass


class InertiaSchemaError(Exception):
    """Raised when Inertia props do not match a render schema."""

    pass
