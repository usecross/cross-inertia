"""
Django settings for Inertia.

This module provides a DRF-style settings pattern for configuring Inertia
in Django projects. Settings are read from Django's settings module.

Usage in settings.py:

    CROSS_INERTIA = {
        'LAYOUT': 'base.html',
        'VITE_ENTRY': 'src/main.tsx',
        'VITE_PORT': 5173,
        'MANIFEST_PATH': BASE_DIR / 'static/build/.vite/manifest.json',
        'SSR_ENABLED': False,
        'SHARE': 'myapp.inertia.share_data',  # Optional: shared data function
    }

Then access settings via:

    from inertia.django.conf import inertia_settings

    template = inertia_settings.LAYOUT
    port = inertia_settings.VITE_PORT
"""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    # Template settings
    "LAYOUT": "base.html",
    # Vite settings
    "VITE_PORT": 5173,
    "VITE_HOST": "localhost",
    "VITE_ENTRY": "src/main.tsx",
    "VITE_COMMAND": "bun run dev",
    "VITE_TIMEOUT": 30.0,
    # Production settings
    "MANIFEST_PATH": "static/build/.vite/manifest.json",
    # SSR settings
    "SSR_ENABLED": False,
    "SSR_URL": "http://127.0.0.1:13714",
    "SSR_COMMAND": "bun dist/ssr/ssr.js",
    "SSR_TIMEOUT": 10.0,
    "SSR_HEALTH_PATH": "/health",
    # Shared data
    "SHARE": None,  # Dotted path to share function, e.g. 'myapp.inertia.share_data'
}


def _find_available_port(start: int = 5173, end: int = 5273) -> int:
    """Find an available port in the given range."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start}-{end}")


class InertiaSettings:
    """
    A settings object that allows Inertia settings to be accessed as properties.

    Settings are read from Django's settings.CROSS_INERTIA dict, with fallback to defaults.
    Values are cached after first access for performance.

    Example:
        from inertia.django.conf import inertia_settings

        # Access settings as attributes
        template = inertia_settings.LAYOUT
        port = inertia_settings.VITE_PORT
    """

    def __init__(self) -> None:
        self._cached_attrs: set[str] = set()
        self._resolved_vite_port: int | None = None

    @property
    def user_settings(self) -> dict[str, Any]:
        """Load user settings from Django settings (cached)."""
        if not hasattr(self, "_user_settings"):
            from django.conf import settings

            self._user_settings = getattr(settings, "CROSS_INERTIA", {})
        return self._user_settings

    def __getattr__(self, attr: str) -> Any:
        if attr.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{attr}'")

        if attr not in DEFAULTS:
            raise AttributeError(f"Invalid Inertia setting: '{attr}'")

        val = self.user_settings.get(attr, DEFAULTS[attr])

        # Convert Path to string for consistency
        if isinstance(val, Path):
            val = str(val)

        # Cache the value
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    @property
    def VITE_DEV_URL(self) -> str:
        """Get the full Vite dev server URL."""
        return f"http://{self.VITE_HOST}:{self.resolved_vite_port}"

    @property
    def resolved_vite_port(self) -> int:
        """Get the resolved Vite port (handles 'auto' port selection)."""
        if self._resolved_vite_port is not None:
            return self._resolved_vite_port

        port = self.VITE_PORT
        if port == "auto":
            self._resolved_vite_port = _find_available_port()
        else:
            self._resolved_vite_port = int(port)

        return self._resolved_vite_port

    @property
    def SSR_HEALTH_URL(self) -> str:
        """Get the full SSR health check URL."""
        return f"{self.SSR_URL}{self.SSR_HEALTH_PATH}"

    def get_vite_command_with_port(self) -> str | list[str]:
        """Get the Vite command with the port argument appended."""
        port = self.resolved_vite_port
        command = self.VITE_COMMAND

        if isinstance(command, list):
            return [*command, "--port", str(port)]
        else:
            return f"{command} --port {port}"

    def reload(self) -> None:
        """
        Reload settings from Django settings.

        Clears cached values so they'll be re-read on next access.
        Useful for testing.
        """
        for attr in self._cached_attrs:
            try:
                delattr(self, attr)
            except AttributeError:
                pass
        self._cached_attrs.clear()
        self._resolved_vite_port = None
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


inertia_settings = InertiaSettings()
