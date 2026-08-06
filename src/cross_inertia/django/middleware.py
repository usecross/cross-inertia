"""Django middleware for Inertia.js shared data and dev server startup."""

from __future__ import annotations

import asyncio
import atexit
import concurrent.futures
import logging
import os
import sys
import threading
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from asgiref.sync import iscoroutinefunction, sync_to_async

from .._ssr import SyncSSRServer
from .._vite import SyncViteProcess, is_port_in_use

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


def _is_runserver_serving_process() -> bool:
    """Return True when running inside the Django process that serves requests."""
    is_runserver = len(sys.argv) > 1 and "runserver" in sys.argv[1]
    if not is_runserver:
        return False

    # With the autoreloader enabled, Django serves requests from the child
    # process where RUN_MAIN=true. With --noreload, RUN_MAIN is unset and the
    # current process is the serving process.
    return os.environ.get("RUN_MAIN") == "true" or "--noreload" in sys.argv


class InertiaMiddleware:
    """
    Django middleware that adds shared data to all Inertia requests.

    When running Django's development server, this middleware can also start
    the Vite dev server automatically.

    Shared data is computed per-request and stored in request._inertia_shared,
    where it can be accessed by the render() function.

    Configuration in settings.py:
        MIDDLEWARE = [
            ...
            'cross_inertia.django.InertiaMiddleware',
        ]

        CROSS_INERTIA = {
            'SHARE': 'myapp.inertia.share_data',  # Import path to share function
        }

    Example share function:
        # myapp/inertia.py
        def share_data(request):
            return {
                'auth': {
                    'user': request.user.username if request.user.is_authenticated else None,
                },
                'flash': dict(request.session.pop('flash', {})),
            }

    The share function can be sync or async:
        async def share_data(request):
            user_data = await get_user_data_async(request.user)
            return {'auth': user_data}
    """

    sync_capable = True
    async_capable = True
    _vite_process: SyncViteProcess | None = None
    _vite_started = False
    _ssr_process: SyncSSRServer | None = None
    _ssr_started = False
    _vite_lock = threading.Lock()
    _ssr_lock = threading.Lock()

    def __init__(
        self,
        get_response: Callable[["HttpRequest"], "HttpResponse"]
        | Callable[["HttpRequest"], Awaitable["HttpResponse"]],
    ):
        self.get_response = get_response
        self._share_func: Callable[["HttpRequest"], dict[str, Any]] | None = None
        self._share_func_loaded = False
        self._is_async_share: bool = False

        # Check if the response handler is async
        if iscoroutinefunction(get_response):
            self._is_async = True
        else:
            self._is_async = False

        type(self)._maybe_start_vite_dev_server()
        type(self)._maybe_start_ssr_server()

    @classmethod
    def _should_manage_servers(cls) -> bool:
        """Return True when this process should own Inertia subprocesses."""
        return _is_runserver_serving_process()

    @classmethod
    def _should_start_vite_dev_server(cls) -> bool:
        """Start the Vite dev server in development mode."""
        from .conf import inertia_settings

        return cls._should_manage_servers() and inertia_settings.is_dev_mode()

    @classmethod
    def _should_start_ssr_server(cls) -> bool:
        """Start standalone SSR outside development mode.

        In dev mode Vite handles SSR via its ``/__inertia_ssr`` endpoint,
        so a standalone server is unnecessary.  Outside dev mode standalone
        SSR is needed when SSR is enabled.
        """
        from .conf import inertia_settings

        if not cls._should_manage_servers():
            return False
        if not inertia_settings.SSR_ENABLED:
            return False
        # In dev mode Vite handles SSR via /__inertia_ssr.
        if inertia_settings.is_dev_mode():
            return False
        return True

    @classmethod
    def _maybe_start_vite_dev_server(cls) -> None:
        """Start the Vite dev server once for Django's development server."""
        if not cls._should_start_vite_dev_server():
            return

        with cls._vite_lock:
            if cls._vite_started:
                return

            cls._vite_started = True
            cls._start_vite_dev_server()

    @classmethod
    def _start_vite_dev_server(cls) -> None:
        """Start the Vite dev server for development."""
        from .conf import inertia_settings

        vite_port = inertia_settings.resolved_vite_port

        if is_port_in_use(vite_port):
            logger.info(
                f"Port {vite_port} is already in use - assuming Vite is running"
            )
            return

        print(f"Starting Vite dev server on port {vite_port}...")

        cls._vite_process = SyncViteProcess(
            command=inertia_settings.VITE_COMMAND,
            port=vite_port,
            startup_timeout=inertia_settings.VITE_TIMEOUT,
        )

        try:
            cls._vite_process.start()
            print(f"Vite dev server running at http://localhost:{vite_port}")
            atexit.register(cls._stop_vite_dev_server)
        except Exception as e:
            logger.error(f"Failed to start Vite: {e}")
            print(f"Failed to start Vite: {e}")
            cls._vite_process = None

    @classmethod
    def _maybe_start_ssr_server(cls) -> None:
        """Start the standalone SSR server once for non-dev Django runs."""
        if not cls._should_start_ssr_server():
            return

        with cls._ssr_lock:
            if cls._ssr_started:
                return

            cls._ssr_started = True
            cls._start_ssr_server()

    @classmethod
    def _start_ssr_server(cls) -> None:
        """Start the standalone SSR server for production."""
        from .conf import inertia_settings

        health_url = inertia_settings.SSR_HEALTH_URL
        cls._ssr_process = SyncSSRServer(
            command=inertia_settings.SSR_COMMAND,
            cwd=inertia_settings.SSR_CWD,
            health_url=health_url,
            startup_timeout=inertia_settings.SSR_TIMEOUT,
        )

        try:
            cls._ssr_process.start()
            print(f"SSR server running at {inertia_settings.SSR_URL}")
            atexit.register(cls._stop_ssr_server)
        except Exception as e:
            logger.error(f"Failed to start SSR server: {e}")
            print(f"Failed to start SSR server: {e}")
            cls._ssr_process = None

    @classmethod
    def _stop_ssr_server(cls) -> None:
        """Stop the SSR server."""
        if cls._ssr_process is not None:
            print("Stopping SSR server...")
            cls._ssr_process.stop()
            cls._ssr_process = None

    @classmethod
    def _stop_vite_dev_server(cls) -> None:
        """Stop the Vite dev server."""
        if cls._vite_process is not None:
            print("Stopping Vite dev server...")
            cls._vite_process.stop()
            cls._vite_process = None

    def _get_share_func(
        self,
    ) -> Callable[["HttpRequest"], dict[str, Any] | Awaitable[dict[str, Any]]] | None:
        """Lazy load the share function from settings."""
        if not self._share_func_loaded:
            from django.utils.module_loading import import_string

            from .conf import inertia_settings

            share_setting = inertia_settings.SHARE
            if share_setting:
                if callable(share_setting):
                    self._share_func = share_setting
                elif isinstance(share_setting, str):
                    self._share_func = import_string(share_setting)

                if self._share_func:
                    self._is_async_share = iscoroutinefunction(self._share_func)

            self._share_func_loaded = True
        return self._share_func

    @staticmethod
    def _adjust_redirect_status(
        request: "HttpRequest", response: "HttpResponse"
    ) -> "HttpResponse":
        """Use a GET-following redirect for non-POST Inertia mutations."""
        is_inertia = request.headers.get("X-Inertia", "").lower() == "true"
        if (
            is_inertia
            and request.method in {"PUT", "PATCH", "DELETE"}
            and response.status_code == 302
        ):
            response.status_code = 303
        return response

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        """Sync middleware entry point."""
        if self._is_async:
            # If get_response is async, we need to return a coroutine
            return self.__acall__(request)  # type: ignore

        # Compute shared data synchronously
        share_func = self._get_share_func()
        if share_func:
            try:
                if self._is_async_share:
                    # Run async share function in sync context
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None

                    if loop:
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future: concurrent.futures.Future[Any] = executor.submit(
                                asyncio.run,  # type: ignore[arg-type]
                                share_func(request),
                            )
                            request._inertia_shared = future.result()  # type: ignore[attr-defined]
                    else:
                        request._inertia_shared = asyncio.run(share_func(request))  # type: ignore
                else:
                    request._inertia_shared = share_func(request)  # type: ignore

                logger.debug(
                    f"Shared data keys: {list(request._inertia_shared.keys())}"  # type: ignore
                )
            except Exception as e:
                logger.error(f"Error computing shared data: {e}", exc_info=True)
                request._inertia_shared = {}  # type: ignore
        else:
            request._inertia_shared = {}  # type: ignore

        response = self.get_response(request)  # type: ignore
        return self._adjust_redirect_status(request, response)

    async def __acall__(self, request: "HttpRequest") -> "HttpResponse":
        """Async middleware entry point."""
        share_func = self._get_share_func()
        if share_func:
            try:
                if self._is_async_share:
                    request._inertia_shared = await share_func(request)  # type: ignore
                else:
                    request._inertia_shared = await sync_to_async(
                        share_func,
                        thread_sensitive=True,
                    )(request)  # type: ignore

                logger.debug(
                    f"Shared data keys: {list(request._inertia_shared.keys())}"  # type: ignore
                )
            except Exception as e:
                logger.error(f"Error computing shared data: {e}", exc_info=True)
                request._inertia_shared = {}  # type: ignore
        else:
            request._inertia_shared = {}  # type: ignore

        response = await self.get_response(request)  # type: ignore
        return self._adjust_redirect_status(request, response)
