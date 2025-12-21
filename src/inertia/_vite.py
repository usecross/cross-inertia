"""Vite dev server process management.

This module provides sync and async implementations for managing the Vite
dev server subprocess. Use the appropriate class based on your framework:

- SyncViteProcess: For sync contexts (Django WSGI, Flask)
- AsyncViteProcess: For async contexts (FastAPI, Litestar, Django ASGI)

Example (sync):
    from inertia._vite import SyncViteProcess

    vite = SyncViteProcess(port=5173)
    vite.start()
    # ... app runs ...
    vite.stop()

Example (async):
    from inertia._vite import AsyncViteProcess

    vite = AsyncViteProcess(port=5173)
    await vite.start()
    # ... app runs ...
    await vite.stop()
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


class BaseViteProcess:
    """Base class with shared Vite configuration and utilities."""

    def __init__(
        self,
        command: str | list[str] = "bun run dev",
        port: int = 5173,
        startup_timeout: float = 30.0,
    ):
        """
        Initialize the Vite process manager.

        Args:
            command: Command to start Vite dev server.
            port: Port for the Vite dev server.
            startup_timeout: Maximum time to wait for server to become healthy.
        """
        self.command = command
        self.port = port
        self.startup_timeout = startup_timeout
        self.health_url = f"http://localhost:{port}/@vite/client"

    def get_command_with_port(self) -> str | list[str]:
        """Get the command with port argument appended."""
        if isinstance(self.command, list):
            return [*self.command, "--port", str(self.port)]
        return f"{self.command} --port {self.port}"


class SyncViteProcess(BaseViteProcess):
    """Sync Vite dev server manager for Django WSGI, Flask, etc."""

    def __init__(
        self,
        command: str | list[str] = "bun run dev",
        port: int = 5173,
        startup_timeout: float = 30.0,
    ):
        super().__init__(command, port, startup_timeout)
        self._process: subprocess.Popen[str] | None = None
        self._output_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the Vite dev server and wait for it to be healthy."""
        if self._process is not None:
            logger.warning("Vite dev server is already running")
            return

        full_command = self.get_command_with_port()
        logger.info(f"Starting Vite dev server: {full_command}")

        # Start the process
        if isinstance(full_command, str):
            self._process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
            )
        else:
            self._process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
            )

        # Start output logging thread
        self._output_thread = threading.Thread(target=self._log_output, daemon=True)
        self._output_thread.start()

        # Wait for health
        self._wait_for_health()
        logger.info(f"Vite dev server running at http://localhost:{self.port}")

    def _log_output(self) -> None:
        """Log Vite output to stdout."""
        if self._process is None or self._process.stdout is None:
            return

        for line in iter(self._process.stdout.readline, ""):
            if self._stop_event.is_set():
                break
            if line:
                print(f"[vite] {line.rstrip()}")

    def _wait_for_health(self) -> None:
        """Wait for Vite to become healthy."""
        import httpx

        start_time = time.time()

        with httpx.Client(timeout=2.0) as client:
            while True:
                elapsed = time.time() - start_time
                if elapsed > self.startup_timeout:
                    self.stop()
                    raise RuntimeError(
                        f"Vite did not start within {self.startup_timeout}s"
                    )

                # Check if process exited
                if self._process is not None and self._process.poll() is not None:
                    raise RuntimeError(
                        f"Vite exited with code {self._process.returncode}"
                    )

                try:
                    response = client.get(self.health_url)
                    if response.status_code == 200:
                        # Wait a moment to ensure process didn't just crash
                        time.sleep(0.3)
                        if (
                            self._process is not None
                            and self._process.poll() is not None
                        ):
                            raise RuntimeError(
                                f"Vite exited with code {self._process.returncode}"
                            )
                        return
                except httpx.ConnectError:
                    pass
                except Exception:
                    pass

                time.sleep(0.1)

    def stop(self) -> None:
        """Stop the Vite dev server."""
        if self._process is None:
            return

        logger.info("Stopping Vite dev server...")
        self._stop_event.set()

        try:
            if sys.platform == "win32":
                self._process.terminate()
            else:
                # Kill the entire process group
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
            logger.error(f"Error stopping Vite: {e}")

        self._process = None
        self._stop_event.clear()

    @property
    def is_running(self) -> bool:
        """Check if the Vite dev server is currently running."""
        return self._process is not None and self._process.poll() is None


class AsyncViteProcess(BaseViteProcess):
    """Async Vite dev server manager for FastAPI, Litestar, Django ASGI, etc."""

    def __init__(
        self,
        command: str | list[str] = "bun run dev",
        port: int = 5173,
        startup_timeout: float = 30.0,
        env: dict[str, str] | None = None,
    ):
        super().__init__(command, port, startup_timeout)
        self.env = env
        self._process: asyncio.subprocess.Process | None = None
        self._output_task: asyncio.Task[Any] | None = None

    async def start(self) -> None:
        """Start the Vite dev server and wait for it to be healthy."""
        if self._process is not None:
            logger.warning("Vite dev server is already running")
            return

        # Prepare environment
        process_env = os.environ.copy()
        if self.env:
            process_env.update(self.env)

        full_command = self.get_command_with_port()
        logger.info(f"Starting Vite dev server: {full_command}")

        # Start subprocess
        try:
            if isinstance(full_command, str):
                self._process = await asyncio.create_subprocess_shell(
                    full_command,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                self._process = await asyncio.create_subprocess_exec(
                    *full_command,
                    env=process_env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Vite dev server command not found: {full_command}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to start Vite dev server: {e}") from e

        # Start a task to log output
        self._output_task = asyncio.create_task(self._log_output())

        # Wait for server to become healthy
        await self._wait_for_health()
        logger.info(f"Vite dev server running at http://localhost:{self.port}")

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
                    logger.debug(f"[vite] {prefix}: {text}")

        if self._process.stdout and self._process.stderr:
            await asyncio.gather(
                read_stream(self._process.stdout, "stdout"),
                read_stream(self._process.stderr, "stderr"),
            )

    async def _wait_for_health(self) -> None:
        """Wait for Vite to become healthy."""
        import httpx

        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=2.0) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.startup_timeout:
                    await self.stop()
                    raise RuntimeError(
                        f"Vite did not start within {self.startup_timeout}s"
                    )

                # Check if process exited
                if self._process is not None and self._process.returncode is not None:
                    raise RuntimeError(
                        f"Vite exited with code {self._process.returncode}"
                    )

                try:
                    response = await client.get(self.health_url)
                    if response.status_code == 200:
                        return
                except httpx.ConnectError:
                    pass
                except Exception:
                    pass

                await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Stop the Vite dev server."""
        if self._process is None:
            return

        logger.info("Stopping Vite dev server...")

        # Cancel output task
        if self._output_task:
            self._output_task.cancel()
            try:
                await self._output_task
            except asyncio.CancelledError:
                pass

        # Terminate process
        try:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.error(f"Error stopping Vite: {e}")

        self._process = None

    @property
    def is_running(self) -> bool:
        """Check if the Vite dev server is currently running."""
        return self._process is not None and self._process.returncode is None
