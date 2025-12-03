"""Lifespan management for Inertia SSR server.

This module provides utilities to automatically start and stop the SSR server
with FastAPI's lifespan context manager.

Example - Simple usage:
    from fastapi import FastAPI
    from inertia import inertia_lifespan

    app = FastAPI(lifespan=inertia_lifespan)

Example - Composable approach:
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from inertia import create_ssr_lifespan

    @asynccontextmanager
    async def lifespan(app):
        async with create_ssr_lifespan(command="bun dist/ssr/ssr.js"):
            # Your other startup logic here
            yield
            # Your other shutdown logic here

    app = FastAPI(lifespan=lifespan)

Example - With Vite dev server (development):
    from inertia import create_ssr_lifespan, create_vite_lifespan

    @asynccontextmanager
    async def lifespan(app):
        async with create_ssr_lifespan(), create_vite_lifespan():
            yield
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


class SSRServerError(Exception):
    """Raised when the SSR server fails to start or encounters an error."""

    pass


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

        # Prepare command
        if isinstance(self.command, str):
            shell = True
            shell_cmd: str = self.command
            logger.info(f"Starting SSR server: {shell_cmd}")
        else:
            shell = False
            exec_cmd: list[str] = self.command
            logger.info(f"Starting SSR server: {exec_cmd}")

        try:
            if shell:
                self._process = await asyncio.create_subprocess_shell(
                    shell_cmd,
                    cwd=self.cwd,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                self._process = await asyncio.create_subprocess_exec(
                    *exec_cmd,
                    cwd=self.cwd,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
        except FileNotFoundError as e:
            raise SSRServerError(
                f"SSR server command not found: {self.command}"
            ) from e
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

        async def read_stream(
            stream: asyncio.StreamReader | None, prefix: str
        ) -> None:
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
    Simple lifespan context manager that starts/stops the SSR server.

    This is designed to be used directly as the lifespan parameter for FastAPI.
    For more control, use create_ssr_lifespan() instead.

    The SSR command can be configured via environment variables:
        - INERTIA_SSR_COMMAND: Command to start SSR server (default: "bun dist/ssr/ssr.js")
        - INERTIA_SSR_CWD: Working directory for SSR server
        - INERTIA_SSR_HEALTH_URL: Health check URL (default: "http://127.0.0.1:13714/health")
        - INERTIA_SSR_TIMEOUT: Startup timeout in seconds (default: 10)

    Args:
        app: The FastAPI application instance.

    Example:
        from fastapi import FastAPI
        from inertia import inertia_lifespan

        app = FastAPI(lifespan=inertia_lifespan)
    """
    command = os.environ.get("INERTIA_SSR_COMMAND", "bun dist/ssr/ssr.js")
    cwd = os.environ.get("INERTIA_SSR_CWD")
    health_url = os.environ.get(
        "INERTIA_SSR_HEALTH_URL", "http://127.0.0.1:13714/health"
    )
    timeout = float(os.environ.get("INERTIA_SSR_TIMEOUT", "10"))

    async with create_ssr_lifespan(
        command=command,
        cwd=cwd,
        health_url=health_url,
        startup_timeout=timeout,
    ):
        yield
