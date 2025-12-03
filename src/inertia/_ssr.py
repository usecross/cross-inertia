"""Internal SSR client for Inertia.js

This is an internal module. To enable SSR, use the `ssr_enabled` flag
on InertiaResponse:

    inertia_response = InertiaResponse(
        ssr_enabled=True,
        ssr_url="http://localhost:13714",  # optional, this is the default
    )

The SSR server must implement the Inertia SSR protocol:
- POST /render - Renders a page and returns {head: [...], body: str}
- GET /health - Returns server health status
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class SSRResponse:
    """Response from the SSR server."""

    head: list[str]
    body: str


class InertiaSSR:
    """SSR client that communicates with a Node.js/Bun SSR server."""

    def __init__(
        self,
        url: str = "http://127.0.0.1:13714",
        timeout: float = 5.0,
        enabled: bool = True,
    ):
        """
        Initialize the SSR client.

        Args:
            url: Base URL of the SSR server
            timeout: Request timeout in seconds
            enabled: Whether SSR is enabled
        """
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.enabled = enabled
        self._client: httpx.AsyncClient | None = None
        self._healthy: bool | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def health_check(self) -> bool:
        """Check if the SSR server is healthy."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.url}/health")
            self._healthy = response.status_code == 200
            if self._healthy:
                logger.info("SSR server is healthy")
            return self._healthy
        except Exception as e:
            logger.warning(f"SSR health check failed: {e}")
            self._healthy = False
            return False

    async def render(self, page: dict[str, Any]) -> SSRResponse | None:
        """
        Render a page using the SSR server.

        Args:
            page: The Inertia page object containing component, props, url, version

        Returns:
            SSRResponse with head tags and body HTML, or None if SSR fails
        """
        if not self.enabled:
            return None

        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.url}/render",
                json=page,
            )
            response.raise_for_status()

            data = response.json()
            result = SSRResponse(
                head=data.get("head", []),
                body=data.get("body", ""),
            )
            logger.debug(f"SSR rendered {page.get('component')} successfully")
            return result

        except httpx.TimeoutException:
            logger.warning(f"SSR request timed out for {page.get('component')}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"SSR request failed with status {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"SSR request failed: {e}")
            return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
