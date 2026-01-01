"""Django app configuration for Inertia."""

from __future__ import annotations

import atexit
import logging
import os
import sys

from django.apps import AppConfig

from .._vite import SyncViteProcess, is_port_in_use

logger = logging.getLogger(__name__)


class InertiaConfig(AppConfig):
    """Django app configuration for inertia.django."""

    name = "inertia.django"
    label = "inertia"
    verbose_name = "Inertia.js"

    _vite_process: SyncViteProcess | None = None

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

        # Check if Vite is already running (e.g., started manually)
        if is_port_in_use(vite_port):
            logger.info(
                f"Port {vite_port} is already in use - assuming Vite is running"
            )
            return

        print(f"Starting Vite dev server on port {vite_port}...")

        self._vite_process = SyncViteProcess(
            command=inertia_settings.VITE_COMMAND,
            port=vite_port,
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
