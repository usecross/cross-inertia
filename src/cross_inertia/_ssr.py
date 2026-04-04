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
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

VITE_DEV_SSR_ENDPOINT = "/__inertia_ssr"


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
        render_path: str = "/render",
        health_path: str = "/health",
    ):
        """
        Initialize the SSR client.

        Args:
            url: Base URL of the SSR server
            timeout: Request timeout in seconds
            enabled: Whether SSR is enabled
            render_path: Path used for SSR render requests
            health_path: Path used for SSR health checks
        """
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.enabled = enabled
        self.render_path = render_path
        self.health_path = health_path
        self._healthy: bool | None = None

    async def health_check(self) -> bool:
        """Check if the SSR server is healthy."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.url}{self.health_path}")
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.url}{self.render_path}",
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


class SyncSSRServer:
    """Sync SSR server manager for Django and other sync frameworks."""

    def __init__(
        self,
        command: str | list[str] = "bun dist/ssr/ssr.js",
        cwd: str | None = None,
        health_url: str = "http://127.0.0.1:13714/health",
        startup_timeout: float = 10.0,
        env: dict[str, str] | None = None,
    ):
        self.command = command
        self.cwd = cwd
        self.health_url = health_url
        self.startup_timeout = startup_timeout
        self.env = env
        self._process: subprocess.Popen[str] | None = None
        self._output_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the SSR server subprocess and wait for it to become healthy."""
        if self._process is not None:
            logger.warning("SSR server is already running")
            return

        process_env = os.environ.copy()
        if self.env:
            process_env.update(self.env)

        try:
            if isinstance(self.command, str):
                logger.info(f"Starting SSR server: {self.command}")
                self._process = subprocess.Popen(
                    self.command,
                    cwd=self.cwd,
                    env=process_env,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid if sys.platform != "win32" else None,
                )
            else:
                logger.info(f"Starting SSR server: {self.command}")
                self._process = subprocess.Popen(
                    self.command,
                    cwd=self.cwd,
                    env=process_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid if sys.platform != "win32" else None,
                )
        except FileNotFoundError as e:
            raise RuntimeError(f"SSR server command not found: {self.command}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to start SSR server: {e}") from e

        self._output_thread = threading.Thread(target=self._log_output, daemon=True)
        self._output_thread.start()
        self._wait_for_health()
        logger.info("SSR server started successfully")

    def _log_output(self) -> None:
        """Log SSR process output to stdout."""
        if self._process is None or self._process.stdout is None:
            return

        for line in iter(self._process.stdout.readline, ""):
            if self._stop_event.is_set():
                break
            if line:
                print(f"[ssr] {line.rstrip()}")

    def _wait_for_health(self) -> None:
        """Wait for the SSR server to become healthy."""
        start_time = time.time()

        with httpx.Client(timeout=2.0) as client:
            while True:
                elapsed = time.time() - start_time
                if elapsed > self.startup_timeout:
                    self.stop()
                    raise RuntimeError(
                        f"SSR server did not become healthy within {self.startup_timeout}s"
                    )

                if self._process is not None and self._process.poll() is not None:
                    raise RuntimeError(
                        f"SSR server exited with code {self._process.returncode}"
                    )

                try:
                    response = client.get(self.health_url)
                    if response.status_code == 200:
                        time.sleep(0.3)
                        if (
                            self._process is not None
                            and self._process.poll() is not None
                        ):
                            raise RuntimeError(
                                f"SSR server exited with code {self._process.returncode}"
                            )
                        return
                except httpx.ConnectError:
                    logger.debug("SSR health check connection refused, retrying...")
                except Exception as exc:
                    logger.debug(f"SSR health check failed: {exc}")

                time.sleep(0.1)

    def stop(self) -> None:
        """Stop the SSR server subprocess."""
        if self._process is None:
            return

        logger.info("Stopping SSR server...")
        self._stop_event.set()

        try:
            if sys.platform == "win32":
                self._process.terminate()
            else:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

            self._process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            if sys.platform == "win32":
                self._process.kill()
            else:
                os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
            self._process.wait()
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.error(f"Error stopping SSR server: {e}")

        self._process = None
        self._stop_event.clear()

    @property
    def is_running(self) -> bool:
        """Check if the SSR server is currently running."""
        return self._process is not None and self._process.poll() is None
