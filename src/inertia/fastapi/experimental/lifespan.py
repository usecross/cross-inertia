"""Lifespan management for Inertia SSR and Vite dev servers.

.. warning::
    This module is experimental and may change in future versions.

This module provides utilities to automatically start and stop the SSR server
and Vite dev server with FastAPI's lifespan context manager.

Example - Simple usage with configure_inertia:
    from fastapi import FastAPI
    from inertia import configure_inertia
    from inertia.fastapi.experimental import inertia_lifespan

    configure_inertia(
        vite_port="auto",  # Finds an available port automatically
        vite_entry="frontend/app.tsx",
    )

    app = FastAPI(lifespan=inertia_lifespan)

Example - Composable approach:
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from inertia.fastapi.experimental import create_ssr_lifespan, create_vite_lifespan

    @asynccontextmanager
    async def lifespan(app):
        async with create_ssr_lifespan(command="bun dist/ssr/ssr.js"):
            async with create_vite_lifespan():
                # Your other startup logic here
                yield
                # Your other shutdown logic here

    app = FastAPI(lifespan=lifespan)
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

from inertia._config import get_config

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


class SSRServerError(Exception):
    """Raised when the SSR server fails to start or encounters an error."""

    pass


class ViteServerError(Exception):
    """Raised when the Vite dev server fails to start or encounters an error."""

    pass


def is_dev_mode() -> bool:
    """
    Detect if the application is running in development mode.

    Returns True if:
    - "dev" is in sys.argv (e.g., `fastapi dev main.py`)
    - INERTIA_DEV environment variable is set to "1" or "true"

    Returns:
        True if in development mode, False otherwise.
    """
    # Check environment variable first (allows explicit override)
    env_dev = os.environ.get("INERTIA_DEV", "").lower()
    if env_dev in ("1", "true"):
        return True
    if env_dev in ("0", "false"):
        return False

    # Auto-detect: "dev" in argv when running `fastapi dev`
    return "dev" in sys.argv


class SSRServer:
    """Manages the SSR server subprocess lifecycle."""

    def __init__(
        self,
        command: str | list[str] = "bun dist/ssr/ssr.js",
        cwd: str | None = None,
        health_url: str = "http://127.0.0.1:13714/health",
        startup_timeout: float = 10.0,
        env: dict[str, str] | None = None,
    ):
        """
        Initialize the SSR server manager.

        Args:
            command: Command to start the SSR server. Can be a string (shell command)
                or a list of arguments.
            cwd: Working directory for the SSR server. Defaults to current directory.
            health_url: URL to check for server health.
            startup_timeout: Maximum time to wait for the server to become healthy.
            env: Additional environment variables for the subprocess.
        """
        self.command = command
        self.cwd = cwd
        self.health_url = health_url
        self.startup_timeout = startup_timeout
        self.env = env
        self._process: asyncio.subprocess.Process | None = None
        self._output_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the SSR server subprocess and wait for it to become healthy."""
        if self._process is not None:
            logger.warning("SSR server is already running")
            return

        # Prepare environment
        process_env = os.environ.copy()
        if self.env:
            process_env.update(self.env)

        # Start subprocess
        try:
            if isinstance(self.command, str):
                logger.info(f"Starting SSR server: {self.command}")
                self._process = await asyncio.create_subprocess_shell(
                    self.command,
                    cwd=self.cwd,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                logger.info(f"Starting SSR server: {self.command}")
                self._process = await asyncio.create_subprocess_exec(
                    *self.command,
                    cwd=self.cwd,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
        except FileNotFoundError as e:
            raise SSRServerError(f"SSR server command not found: {self.command}") from e
        except Exception as e:
            raise SSRServerError(f"Failed to start SSR server: {e}") from e

        # Start a task to log output
        self._output_task = asyncio.create_task(self._log_output())

        # Wait for server to become healthy
        await self._wait_for_health()
        logger.info("SSR server started successfully")

    async def _log_output(self) -> None:
        """Log stdout and stderr from the SSR server."""
        if self._process is None:
            return

        async def read_stream(stream: asyncio.StreamReader | None, prefix: str) -> None:
            if stream is None:
                return
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                if text:
                    logger.debug(f"SSR {prefix}: {text}")

        if self._process.stdout and self._process.stderr:
            await asyncio.gather(
                read_stream(self._process.stdout, "stdout"),
                read_stream(self._process.stderr, "stderr"),
            )

    async def _wait_for_health(self) -> None:
        """Wait for the SSR server to become healthy."""
        import httpx

        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=2.0) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.startup_timeout:
                    await self.stop()
                    raise SSRServerError(
                        f"SSR server did not become healthy within {self.startup_timeout}s"
                    )

                # Check if process has exited
                if self._process is not None and self._process.returncode is not None:
                    stderr_output = ""
                    if self._process.stderr:
                        try:
                            stderr_data = await asyncio.wait_for(
                                self._process.stderr.read(), timeout=1.0
                            )
                            stderr_output = stderr_data.decode()
                        except asyncio.TimeoutError:
                            pass
                    raise SSRServerError(
                        f"SSR server exited with code {self._process.returncode}: "
                        f"{stderr_output}"
                    )

                try:
                    response = await client.get(self.health_url)
                    if response.status_code == 200:
                        return
                except httpx.ConnectError:
                    # Server not ready yet
                    pass
                except Exception as e:
                    logger.debug(f"Health check failed: {e}")

                await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Stop the SSR server subprocess gracefully."""
        if self._process is None:
            return

        logger.info("Stopping SSR server...")

        # Cancel the output logging task
        if self._output_task:
            self._output_task.cancel()
            try:
                await self._output_task
            except asyncio.CancelledError:
                pass
            self._output_task = None

        # Try graceful shutdown first
        try:
            if sys.platform == "win32":
                self._process.terminate()
            else:
                self._process.send_signal(signal.SIGTERM)

            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("SSR server did not stop gracefully, forcing kill")
                self._process.kill()
                await self._process.wait()
        except ProcessLookupError:
            # Process already exited
            pass
        except Exception as e:
            logger.error(f"Error stopping SSR server: {e}")

        self._process = None
        logger.info("SSR server stopped")

    @property
    def is_running(self) -> bool:
        """Check if the SSR server is currently running."""
        return self._process is not None and self._process.returncode is None


class ViteDevServer:
    """Manages the Vite dev server subprocess lifecycle."""

    def __init__(
        self,
        command: str | list[str] = "bun run dev",
        health_url: str = "http://localhost:5173",
        startup_timeout: float = 30.0,
        env: dict[str, str] | None = None,
    ):
        """
        Initialize the Vite dev server manager.

        Args:
            command: Command to start the Vite dev server. Can be a string (shell command)
                or a list of arguments. Defaults to "bun run dev".
            health_url: URL to check for server health (Vite dev server URL).
            startup_timeout: Maximum time to wait for the server to become healthy.
            env: Additional environment variables for the subprocess.
        """
        self.command = command
        self.health_url = health_url
        self.startup_timeout = startup_timeout
        self.env = env
        self._process: asyncio.subprocess.Process | None = None
        self._output_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the Vite dev server subprocess and wait for it to become healthy."""
        if self._process is not None:
            logger.warning("Vite dev server is already running")
            return

        # Prepare environment
        process_env = os.environ.copy()
        if self.env:
            process_env.update(self.env)

        # Start subprocess
        try:
            if isinstance(self.command, str):
                logger.info(f"Starting Vite dev server: {self.command}")
                self._process = await asyncio.create_subprocess_shell(
                    self.command,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                logger.info(f"Starting Vite dev server: {self.command}")
                self._process = await asyncio.create_subprocess_exec(
                    *self.command,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
        except FileNotFoundError as e:
            raise ViteServerError(
                f"Vite dev server command not found: {self.command}"
            ) from e
        except Exception as e:
            raise ViteServerError(f"Failed to start Vite dev server: {e}") from e

        # Start a task to log output
        self._output_task = asyncio.create_task(self._log_output())

        # Wait for server to become healthy
        await self._wait_for_health()
        logger.info("Vite dev server started successfully")

    async def _log_output(self) -> None:
        """Log stdout and stderr from the Vite dev server."""
        if self._process is None:
            return

        async def read_stream(stream: asyncio.StreamReader | None, prefix: str) -> None:
            if stream is None:
                return
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                if text:
                    logger.debug(f"Vite {prefix}: {text}")

        if self._process.stdout and self._process.stderr:
            await asyncio.gather(
                read_stream(self._process.stdout, "stdout"),
                read_stream(self._process.stderr, "stderr"),
            )

    async def _wait_for_health(self) -> None:
        """Wait for the Vite dev server to become healthy."""
        import httpx

        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=2.0) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.startup_timeout:
                    await self.stop()
                    raise ViteServerError(
                        f"Vite dev server did not become healthy within "
                        f"{self.startup_timeout}s"
                    )

                # Check if process has exited
                if self._process is not None and self._process.returncode is not None:
                    stderr_output = ""
                    if self._process.stderr:
                        try:
                            stderr_data = await asyncio.wait_for(
                                self._process.stderr.read(), timeout=1.0
                            )
                            stderr_output = stderr_data.decode()
                        except asyncio.TimeoutError:
                            pass
                    raise ViteServerError(
                        f"Vite dev server exited with code {self._process.returncode}: "
                        f"{stderr_output}"
                    )

                try:
                    response = await client.get(self.health_url)
                    # Vite returns HTML, just check for any successful response
                    if response.status_code == 200:
                        return
                except httpx.ConnectError:
                    # Server not ready yet
                    pass
                except Exception as e:
                    logger.debug(f"Vite health check failed: {e}")

                await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Stop the Vite dev server subprocess gracefully."""
        if self._process is None:
            return

        logger.info("Stopping Vite dev server...")

        # Cancel the output logging task
        if self._output_task:
            self._output_task.cancel()
            try:
                await self._output_task
            except asyncio.CancelledError:
                pass
            self._output_task = None

        # Try graceful shutdown first
        try:
            if sys.platform == "win32":
                self._process.terminate()
            else:
                self._process.send_signal(signal.SIGTERM)

            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Vite dev server did not stop gracefully, forcing kill")
                self._process.kill()
                await self._process.wait()
        except ProcessLookupError:
            # Process already exited
            pass
        except Exception as e:
            logger.error(f"Error stopping Vite dev server: {e}")

        self._process = None
        logger.info("Vite dev server stopped")

    @property
    def is_running(self) -> bool:
        """Check if the Vite dev server is currently running."""
        return self._process is not None and self._process.returncode is None


@asynccontextmanager
async def create_vite_lifespan(
    command: str | list[str] = "bun run dev",
    health_url: str = "http://localhost:5173",
    startup_timeout: float = 30.0,
    env: dict[str, str] | None = None,
) -> AsyncGenerator[ViteDevServer, None]:
    """
    Create an async context manager for Vite dev server lifecycle management.

    This is the composable approach that can be used with other lifespan
    managers in your application.

    Args:
        command: Command to start the Vite dev server. Defaults to "bun run dev".
        health_url: URL to check for server health.
        startup_timeout: Maximum time to wait for the server to become healthy.
        env: Additional environment variables for the subprocess.

    Yields:
        The ViteDevServer instance managing the subprocess.

    Example:
        @asynccontextmanager
        async def lifespan(app):
            async with create_vite_lifespan() as vite:
                print(f"Vite running: {vite.is_running}")
                yield

        app = FastAPI(lifespan=lifespan)
    """
    server = ViteDevServer(
        command=command,
        health_url=health_url,
        startup_timeout=startup_timeout,
        env=env,
    )

    await server.start()
    try:
        yield server
    finally:
        await server.stop()


@asynccontextmanager
async def create_ssr_lifespan(
    command: str | list[str] = "bun dist/ssr/ssr.js",
    cwd: str | None = None,
    health_url: str = "http://127.0.0.1:13714/health",
    startup_timeout: float = 10.0,
    env: dict[str, str] | None = None,
) -> AsyncGenerator[SSRServer, None]:
    """
    Create an async context manager for SSR server lifecycle management.

    This is the composable approach that can be used with other lifespan
    managers in your application.

    Args:
        command: Command to start the SSR server. Defaults to "bun dist/ssr/ssr.js".
        cwd: Working directory for the SSR server.
        health_url: URL to check for server health.
        startup_timeout: Maximum time to wait for the server to become healthy.
        env: Additional environment variables for the subprocess.

    Yields:
        The SSRServer instance managing the subprocess.

    Example:
        @asynccontextmanager
        async def lifespan(app):
            async with create_ssr_lifespan() as ssr:
                print(f"SSR running: {ssr.is_running}")
                yield

        app = FastAPI(lifespan=lifespan)
    """
    server = SSRServer(
        command=command,
        cwd=cwd,
        health_url=health_url,
        startup_timeout=startup_timeout,
        env=env,
    )

    await server.start()
    try:
        yield server
    finally:
        await server.stop()


@asynccontextmanager
async def inertia_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Simple lifespan context manager that starts/stops Inertia servers.

    In development mode (detected via `fastapi dev` or INERTIA_DEV=1):
    - Starts the Vite dev server for HMR

    In production mode (or when SSR is enabled):
    - Starts the SSR server

    This is designed to be used directly as the lifespan parameter for FastAPI.
    For more control, use create_ssr_lifespan() and create_vite_lifespan() instead.

    Configuration is read from configure_inertia() if called, otherwise falls back
    to environment variables for backwards compatibility.

    Recommended usage with configure_inertia():
        from inertia import configure_inertia
        from inertia.fastapi.experimental import inertia_lifespan

        configure_inertia(
            vite_port="auto",  # Finds an available port
            vite_entry="frontend/app.tsx",
        )

        app = FastAPI(lifespan=inertia_lifespan)

    Environment variables (fallback):
        Development:
        - INERTIA_DEV: Set to "1" or "true" to force dev mode, "0" or "false" to disable
        - INERTIA_VITE_COMMAND: Command to start Vite (default: "bun run dev")
        - INERTIA_VITE_URL: Vite dev server URL (default: "http://localhost:5173")
        - INERTIA_VITE_TIMEOUT: Startup timeout in seconds (default: 30)

        SSR (production):
        - INERTIA_SSR_ENABLED: Set to "0" or "false" to disable SSR (default: enabled)
        - INERTIA_SSR_COMMAND: Command to start SSR server (default: "bun dist/ssr/ssr.js")
        - INERTIA_SSR_HEALTH_URL: Health check URL (default: "http://127.0.0.1:13714/health")
        - INERTIA_SSR_TIMEOUT: Startup timeout in seconds (default: 10)

    Args:
        app: The FastAPI application instance.
    """
    config = get_config()
    dev_mode = is_dev_mode()

    # Vite dev server (only in dev mode)
    vite_server: ViteDevServer | None = None
    if dev_mode:
        # Use config values, fall back to env vars for backwards compatibility
        vite_command = (
            os.environ.get("INERTIA_VITE_COMMAND")
            or config.get_vite_command_with_port()
        )
        vite_url = os.environ.get("INERTIA_VITE_URL") or config.vite_dev_url
        vite_timeout = float(
            os.environ.get("INERTIA_VITE_TIMEOUT") or config.vite_timeout
        )

        vite_server = ViteDevServer(
            command=vite_command,
            health_url=vite_url,
            startup_timeout=vite_timeout,
        )
        await vite_server.start()

    # SSR server (in production, or when explicitly enabled via config)
    ssr_enabled_env = os.environ.get("INERTIA_SSR_ENABLED", "").lower()
    if ssr_enabled_env:
        ssr_enabled = ssr_enabled_env not in ("0", "false")
    else:
        ssr_enabled = config.ssr_enabled and not dev_mode

    ssr_server: SSRServer | None = None
    if ssr_enabled:
        # Use config values, fall back to env vars for backwards compatibility
        ssr_command = os.environ.get("INERTIA_SSR_COMMAND") or config.ssr_command
        ssr_cwd = os.environ.get("INERTIA_SSR_CWD") or config.ssr_cwd
        ssr_health_url = (
            os.environ.get("INERTIA_SSR_HEALTH_URL") or config.ssr_health_url
        )
        ssr_timeout = float(os.environ.get("INERTIA_SSR_TIMEOUT") or config.ssr_timeout)

        ssr_server = SSRServer(
            command=ssr_command,
            cwd=ssr_cwd,
            health_url=ssr_health_url,
            startup_timeout=ssr_timeout,
        )
        await ssr_server.start()

    try:
        yield
    finally:
        if ssr_server:
            await ssr_server.stop()
        if vite_server:
            await vite_server.stop()
