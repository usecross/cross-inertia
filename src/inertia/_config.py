"""Unified configuration for Cross-Inertia.

This module provides a single source of truth for all Inertia configuration,
including Vite dev server, SSR, and template settings.

Example:
    from inertia import configure_inertia

    # Basic configuration (uses default vite_entry="frontend/app.tsx")
    configure_inertia(
        template_dir="templates",
    )

    # With auto port selection (finds an unused port)
    configure_inertia(
        vite_port="auto",
    )

    # Full configuration
    configure_inertia(
        vite_port=5173,
        vite_entry="frontend/app.tsx",
        vite_command="bun run dev",
        template_dir="templates",
        ssr_enabled=True,
        ssr_url="http://127.0.0.1:13714",
    )
"""

from __future__ import annotations

import logging
import socket
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


def find_available_port(start: int = 5173, end: int = 5273) -> int:
    """Find an available port in the given range.

    Args:
        start: Start of port range (inclusive)
        end: End of port range (exclusive)

    Returns:
        An available port number

    Raises:
        RuntimeError: If no available port is found in the range
    """
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                logger.debug(f"Found available port: {port}")
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start}-{end}")


@dataclass
class InertiaConfig:
    """Configuration for Cross-Inertia.

    This is the single source of truth for all configuration. Both the
    InertiaResponse (for template rendering) and the lifespan managers
    (for starting servers) read from this config.
    """

    # Vite settings
    vite_port: int | Literal["auto"] = 5173
    """Port for Vite dev server. Use "auto" to find an available port."""

    vite_host: str = "localhost"
    """Host for Vite dev server."""

    vite_entry: str = "frontend/app.tsx"
    """Entry point for Vite (e.g., 'frontend/app.tsx', 'src/main.tsx')."""

    vite_command: str | list[str] = "bun run dev"
    """Command to start Vite dev server. Port will be appended automatically."""

    vite_timeout: float = 30.0
    """Timeout in seconds for Vite dev server startup."""

    # Template settings
    template_dir: str = "templates"
    """Directory containing Jinja2 templates."""

    manifest_path: str = "static/build/.vite/manifest.json"
    """Path to Vite manifest file for production builds."""

    # SSR settings
    ssr_enabled: bool = False
    """Whether SSR is enabled."""

    ssr_url: str = "http://127.0.0.1:13714"
    """URL of the SSR server."""

    ssr_command: str | list[str] = "bun dist/ssr/ssr.js"
    """Command to start the SSR server."""

    ssr_cwd: str | None = None
    """Working directory for SSR server."""

    ssr_timeout: float = 10.0
    """Timeout in seconds for SSR server startup."""

    ssr_health_path: str = "/health"
    """Health check path for SSR server."""

    # Internal state (set after initialization)
    _resolved_vite_port: int | None = field(default=None, repr=False)

    @property
    def vite_dev_url(self) -> str:
        """Get the full Vite dev server URL."""
        port = self.resolved_vite_port
        return f"http://{self.vite_host}:{port}"

    @property
    def resolved_vite_port(self) -> int:
        """Get the resolved Vite port (handles 'auto' port selection)."""
        if self._resolved_vite_port is not None:
            return self._resolved_vite_port

        if self.vite_port == "auto":
            self._resolved_vite_port = find_available_port()
            logger.info(f"Auto-selected Vite port: {self._resolved_vite_port}")
        else:
            self._resolved_vite_port = self.vite_port

        return self._resolved_vite_port

    @property
    def ssr_health_url(self) -> str:
        """Get the full SSR health check URL."""
        return f"{self.ssr_url}{self.ssr_health_path}"

    def get_vite_command_with_port(self) -> str | list[str]:
        """Get the Vite command with the port argument appended."""
        port = self.resolved_vite_port

        if isinstance(self.vite_command, list):
            return [*self.vite_command, "--port", str(port)]
        else:
            return f"{self.vite_command} --port {port}"


# Global configuration instance
_config: InertiaConfig | None = None


def configure_inertia(
    *,
    vite_port: int | Literal["auto"] = 5173,
    vite_host: str = "localhost",
    vite_entry: str = "frontend/app.tsx",
    vite_command: str | list[str] = "bun run dev",
    vite_timeout: float = 30.0,
    template_dir: str = "templates",
    manifest_path: str = "static/build/.vite/manifest.json",
    ssr_enabled: bool = False,
    ssr_url: str = "http://127.0.0.1:13714",
    ssr_command: str | list[str] = "bun dist/ssr/ssr.js",
    ssr_timeout: float = 10.0,
    ssr_health_path: str = "/health",
) -> InertiaConfig:
    """Configure Cross-Inertia with a single function call.

    This sets up both the template rendering (InertiaResponse) and the
    lifespan managers (Vite/SSR servers) with consistent configuration.

    Args:
        vite_port: Port for Vite dev server. Use "auto" to find an available port.
        vite_host: Host for Vite dev server.
        vite_entry: Entry point for Vite (e.g., 'frontend/app.tsx', 'src/main.tsx').
        vite_command: Command to start Vite dev server.
        vite_timeout: Timeout for Vite server startup.
        template_dir: Directory containing Jinja2 templates.
        manifest_path: Path to Vite manifest for production.
        ssr_enabled: Whether to enable SSR.
        ssr_url: URL of the SSR server.
        ssr_command: Command to start the SSR server.
        ssr_timeout: Timeout for SSR server startup.
        ssr_health_path: Health check path for SSR server.

    Returns:
        The InertiaConfig instance.

    Example:
        from inertia import configure_inertia

        # Auto port selection - finds unused port automatically
        configure_inertia(
            vite_port="auto",
        )

        # Explicit configuration
        configure_inertia(
            vite_port=5188,
            vite_entry="src/main.tsx",
            ssr_enabled=True,
        )
    """
    global _config

    _config = InertiaConfig(
        vite_port=vite_port,
        vite_host=vite_host,
        vite_entry=vite_entry,
        vite_command=vite_command,
        vite_timeout=vite_timeout,
        template_dir=template_dir,
        manifest_path=manifest_path,
        ssr_enabled=ssr_enabled,
        ssr_url=ssr_url,
        ssr_command=ssr_command,
        ssr_timeout=ssr_timeout,
        ssr_health_path=ssr_health_path,
    )

    logger.info(
        f"Inertia configured: vite_port={_config.resolved_vite_port}, ssr_enabled={ssr_enabled}"
    )
    return _config


def get_config() -> InertiaConfig:
    """Get the current Inertia configuration.

    Returns a default configuration if configure_inertia() hasn't been called.
    """
    global _config
    if _config is None:
        _config = InertiaConfig()
    return _config


def reset_config() -> None:
    """Reset the configuration to None. Useful for testing."""
    global _config
    _config = None
