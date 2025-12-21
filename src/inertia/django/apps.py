"""Django app configuration for Inertia."""

from __future__ import annotations

import atexit
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


class ViteProcess:
    """Manages the Vite dev server subprocess."""

    def __init__(
        self,
        command: str | list[str],
        health_url: str,
        startup_timeout: float = 30.0,
    ):
        self.command = command
        self.health_url = health_url
        self.startup_timeout = startup_timeout
        self._process: subprocess.Popen | None = None
        self._output_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the Vite dev server and wait for it to be healthy."""
        if self._process is not None:
            return

        # Start the process
        if isinstance(self.command, str):
            self._process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
            )
        else:
            self._process = subprocess.Popen(
                self.command,
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
                        # Wait a moment to ensure our process didn't just crash
                        time.sleep(0.3)
                        if self._process is not None and self._process.poll() is not None:
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
            print(f"Error stopping Vite: {e}")

        self._process = None


class InertiaConfig(AppConfig):
    """Django app configuration for inertia.django."""

    name = "inertia.django"
    label = "inertia"
    verbose_name = "Inertia.js"

    _vite_process: ViteProcess | None = None

    def ready(self) -> None:
        """Initialize Inertia when Django starts.

        Automatically starts the Vite dev server when using Django's runserver.
        """
        # Detect if we're running Django's development server
        is_runserver = len(sys.argv) > 1 and "runserver" in sys.argv[1]

        # Only start Vite in the parent process (not the reloader child)
        # Django's reloader spawns a child process with RUN_MAIN=true
        is_parent = os.environ.get("RUN_MAIN") != "true"

        if is_runserver and is_parent:
            self._start_vite_dev_server()

    def _start_vite_dev_server(self) -> None:
        """Start the Vite dev server for development."""
        from .conf import inertia_settings

        # Get Vite settings
        vite_port = inertia_settings.resolved_vite_port
        vite_command = inertia_settings.get_vite_command_with_port()
        health_url = f"http://localhost:{vite_port}/@vite/client"

        # Check if Vite is already running (e.g., started manually)
        if _is_port_in_use(vite_port):
            logger.info(
                f"Port {vite_port} is already in use - assuming Vite is running"
            )
            return

        logger.info(f"Starting Vite dev server on port {vite_port}...")
        print(f"Starting Vite dev server on port {vite_port}...")

        self._vite_process = ViteProcess(
            command=vite_command,
            health_url=health_url,
            startup_timeout=inertia_settings.VITE_TIMEOUT,
        )

        try:
            self._vite_process.start()
            print(f"Vite dev server running at http://localhost:{vite_port}")

            # Register cleanup on exit
            atexit.register(self._stop_vite_dev_server)

        except Exception as e:
            logger.error(f"Failed to start Vite: {e}")
            print(f"Failed to start Vite: {e}")
            self._vite_process = None

    def _stop_vite_dev_server(self) -> None:
        """Stop the Vite dev server."""
        if self._vite_process is not None:
            print("Stopping Vite dev server...")
            self._vite_process.stop()
            self._vite_process = None
