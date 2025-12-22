"""Django middleware for Inertia.js shared data."""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class InertiaMiddleware:
    """
    Django middleware that adds shared data to all Inertia requests.

    Shared data is computed per-request and stored in request._inertia_shared,
    where it can be accessed by the render() function.

    Configuration in settings.py:
        MIDDLEWARE = [
            ...
            'inertia.django.InertiaMiddleware',
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
        if asyncio.iscoroutinefunction(get_response):
            self._is_async = True
        else:
            self._is_async = False

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
                    self._is_async_share = asyncio.iscoroutinefunction(self._share_func)

            self._share_func_loaded = True
        return self._share_func

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

        return self.get_response(request)  # type: ignore

    async def __acall__(self, request: "HttpRequest") -> "HttpResponse":
        """Async middleware entry point."""
        share_func = self._get_share_func()
        if share_func:
            try:
                if self._is_async_share:
                    request._inertia_shared = await share_func(request)  # type: ignore
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

        return await self.get_response(request)  # type: ignore
