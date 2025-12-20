"""
Django management command to run both Vite dev server and Django runserver.

This is an experimental feature that allows you to start both servers with
a single command for development.

Usage:
    python manage.py rundev

Options:
    --vite-command: Command to start Vite (default: "bun run dev")
    --vite-port: Port for Vite dev server (default: from config or 5173)
    --django-port: Port for Django server (default: 8000)
    --no-vite: Skip starting Vite (useful if you want to run Vite separately)
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from typing import TYPE_CHECKING

import socket

import httpx
from django.core.management import call_command
from django.core.management.base import BaseCommand

from inertia._config import get_config

if TYPE_CHECKING:
    pass


def is_port_in_use(port: int, host: str = "localhost") -> bool:
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


class Command(BaseCommand):
    help = "Run Django development server with Vite dev server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--vite-command",
            type=str,
            default=None,
            help="Command to start Vite dev server (default: from config or 'bun run dev')",
        )
        parser.add_argument(
            "--vite-port",
            type=int,
            default=None,
            help="Port for Vite dev server (default: from config or 5173)",
        )
        parser.add_argument(
            "--django-port",
            type=str,
            default="8000",
            help="Port for Django server (default: 8000)",
        )
        parser.add_argument(
            "--no-vite",
            action="store_true",
            help="Skip starting Vite dev server",
        )

    def handle(self, *args, **options):
        config = get_config()

        # Django's reloader spawns a child process with RUN_MAIN=true
        # We only want to start Vite in the parent process
        is_reloader_child = os.environ.get("RUN_MAIN") == "true"

        vite_process = None

        if not options["no_vite"] and not is_reloader_child:
            # Determine Vite settings
            vite_port = options["vite_port"] or config.resolved_vite_port
            vite_command = options["vite_command"]

            if vite_command is None:
                # Build command with port
                base_command = config.vite_command
                if isinstance(base_command, list):
                    vite_command = [*base_command, "--port", str(vite_port)]
                else:
                    vite_command = f"{base_command} --port {vite_port}"

            health_url = f"http://localhost:{vite_port}/@vite/client"

            # Check if port is already in use
            if is_port_in_use(vite_port):
                self.stderr.write(
                    self.style.ERROR(
                        f"Port {vite_port} is already in use. "
                        f"Kill the existing process or use --vite-port to specify a different port."
                    )
                )
                return

            self.stdout.write(f"Starting Vite dev server on port {vite_port}...")
            vite_process = ViteProcess(
                command=vite_command,
                health_url=health_url,
                startup_timeout=config.vite_timeout,
            )

            try:
                vite_process.start()
                self.stdout.write(
                    self.style.SUCCESS(f"Vite dev server running at http://localhost:{vite_port}")
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to start Vite: {e}"))
                return

        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            self.stdout.write("\nShutting down...")
            if vite_process:
                vite_process.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Check if Django port is in use (only in parent process)
        django_port = int(options["django_port"])
        if not is_reloader_child and is_port_in_use(django_port):
            self.stderr.write(
                self.style.ERROR(
                    f"Port {django_port} is already in use. "
                    f"Kill the existing process or use --django-port to specify a different port."
                )
            )
            if vite_process:
                vite_process.stop()
            return

        try:
            # Run Django's runserver
            if not is_reloader_child:
                self.stdout.write(f"Starting Django server on port {django_port}...")
            call_command("runserver", str(django_port), use_reloader=True)
        finally:
            if vite_process:
                vite_process.stop()
