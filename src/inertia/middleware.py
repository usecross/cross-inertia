"""Inertia middleware for sharing data across all requests."""

import asyncio
import logging
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class InertiaMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds shared data to all Inertia requests.

    Shared data is computed per-request and stored in request.state.inertia_shared,
    where it can be accessed by the Inertia.render() method.

    Example usage:
        ```python
        from inertia.middleware import InertiaMiddleware

        def share_data(request: Request) -> dict:
            return {
                "auth": {"user": get_current_user(request)},
                "flash": request.session.get("flash", {}),
            }

        app.add_middleware(InertiaMiddleware, share=share_data)
        ```
    """

    def __init__(
        self,
        app,
        share: Callable[[Request], dict[str, Any]]
        | Callable[[Request], Awaitable[dict[str, Any]]]
        | None = None,
    ):
        """
        Initialize the middleware with an optional share function.

        Args:
            app: The ASGI application
            share: A function that takes a Request and returns a dict of shared data.
                   Can be sync or async. If None, no shared data will be added.
        """
        super().__init__(app)
        self.share_func = share
        self._is_async = share is not None and asyncio.iscoroutinefunction(share)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and inject shared data into request.state.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the next handler
        """
        # Resolve shared data (support both sync and async functions)
        shared_data: dict[str, Any] = {}

        if self.share_func is not None:
            try:
                if self._is_async:
                    shared_data = await self.share_func(request)  # type: ignore
                else:
                    shared_data = self.share_func(request)  # type: ignore

                logger.debug(f"Shared data keys: {list(shared_data.keys())}")

            except Exception as e:
                logger.error(f"Error computing shared data: {e}", exc_info=True)

        # Store in request.state so it's accessible in routes
        request.state.inertia_shared = shared_data

        # Continue processing the request
        response = await call_next(request)
        return response
