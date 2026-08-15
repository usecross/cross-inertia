"""
Django settings for Inertia.

This module provides a DRF-style settings pattern for configuring Inertia
in Django projects. Settings are read from Django's settings module.

Usage in settings.py:

    CROSS_INERTIA = {
        'LAYOUT': 'base.html',
        'VITE_ENTRY': 'frontend/app.tsx',
        'VITE_PORT': 'auto',  # or a fixed port number
        'MANIFEST_PATH': BASE_DIR / 'static/build/.vite/manifest.json',
        'SSR_ENABLED': False,
        'SHARE': 'myapp.inertia.share_data',  # Optional: shared data function
    }

The settings backed by ``InertiaConfig`` share its defaults so the Django and
FastAPI adapters behave the same out of the box. ``ASSET_URL_PREFIX`` remains
Django-aware and derives from ``STATIC_URL`` unless explicitly configured.

Then access settings via:

    from cross_inertia.django.conf import inertia_settings

    template = inertia_settings.LAYOUT
    port = inertia_settings.VITE_PORT
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from cross_inertia._config import (
    InertiaConfig,
    find_available_port,
    get_config,
    is_config_explicitly_set,
)

# Django settings that mirror an ``InertiaConfig`` field. Their defaults are
# read from ``InertiaConfig`` so both adapters stay in sync, and when
# ``configure_inertia()`` was called its values win over these defaults.
SHARED_CONFIG_ATTRS: dict[str, str] = {
    "VITE_PORT": "vite_port",
    "VITE_HOST": "vite_host",
    "VITE_ENTRY": "vite_entry",
    "VITE_COMMAND": "vite_command",
    "VITE_BASE": "vite_base",
    "VITE_TIMEOUT": "vite_timeout",
    "VITE_REACT_REFRESH": "vite_react_refresh",
    "MANIFEST_PATH": "manifest_path",
    "ASSET_URL_PREFIX": "asset_url_prefix",
    "SSR_ENABLED": "ssr_enabled",
    "SSR_URL": "ssr_url",
    "SSR_COMMAND": "ssr_command",
    "SSR_TIMEOUT": "ssr_timeout",
    "SSR_HEALTH_PATH": "ssr_health_path",
    "SSR_CWD": "ssr_cwd",
}

_SHARED_DEFAULTS = InertiaConfig()

DEFAULTS: dict[str, Any] = {
    # Template settings
    "LAYOUT": "base.html",
    # Vite / production / SSR settings shared with configure_inertia()
    **{
        key: getattr(_SHARED_DEFAULTS, attr)
        for key, attr in SHARED_CONFIG_ATTRS.items()
    },
    # Shared data
    "SHARE": None,  # Dotted path to share function, e.g. 'myapp.inertia.share_data'
}


class InertiaSettings:
    """
    A settings object that allows Inertia settings to be accessed as properties.

    Settings are read from Django's settings.CROSS_INERTIA dict, with fallback to defaults.
    Values are cached after first access for performance.

    Example:
        from cross_inertia.django.conf import inertia_settings

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

        if attr in self.user_settings:
            val = self.user_settings[attr]
        elif attr in SHARED_CONFIG_ATTRS and is_config_explicitly_set():
            val = getattr(get_config(), SHARED_CONFIG_ATTRS[attr])
        elif attr == "ASSET_URL_PREFIX":
            from django.conf import settings

            static_url = getattr(settings, "STATIC_URL", None) or "/static/"
            if static_url.startswith(("http://", "https://")):
                val = f"{static_url.rstrip('/')}/build"
            else:
                normalized_static_url = static_url.rstrip("/")
                if not normalized_static_url.startswith("/"):
                    normalized_static_url = f"/{normalized_static_url}"
                val = f"{normalized_static_url}/build"
        else:
            val = DEFAULTS[attr]

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
            self._resolved_vite_port = find_available_port()
        else:
            self._resolved_vite_port = int(port)

        return self._resolved_vite_port

    @property
    def SSR_HEALTH_URL(self) -> str:
        """Get the full SSR health check URL."""
        return f"{self.SSR_URL}{self.SSR_HEALTH_PATH}"

    def is_dev_mode(self) -> bool:
        """Determine whether Django should manage Inertia in dev mode."""
        env_dev = os.environ.get("INERTIA_DEV", "").lower()
        if env_dev in ("1", "true"):
            return True
        if env_dev in ("0", "false"):
            return False

        from django.conf import settings

        return bool(getattr(settings, "DEBUG", False))

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
