"""Decorator for FastAPI dependency-based Inertia shared data."""

import functools
import inspect
from typing import Any, Callable

from starlette.requests import Request


def _merge_shared(request: Request, result: dict[str, Any] | None) -> None:
    if result:
        existing = getattr(request.state, "inertia_shared", {})
        request.state.inertia_shared = {**existing, **result}


def inertia_share(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a function as an Inertia shared data provider.

    The return value is merged into ``request.state.inertia_shared``.
    If the function doesn't declare ``request: Request``, one is auto-injected.
    """
    sig = inspect.signature(fn)
    has_request = any(p.annotation is Request for p in sig.parameters.values())
    is_async = inspect.iscoroutinefunction(fn)

    if is_async:

        @functools.wraps(fn)
        async def async_wrapper(**kwargs: Any) -> None:
            request: Request = kwargs["request"]
            if has_request:
                result = await fn(**kwargs)
            else:
                result = await fn(**{k: v for k, v in kwargs.items() if k != "request"})
            _merge_shared(request, result)

        wrapper: Any = async_wrapper
    else:

        @functools.wraps(fn)
        def sync_wrapper(**kwargs: Any) -> None:
            request: Request = kwargs["request"]
            if has_request:
                result = fn(**kwargs)
            else:
                result = fn(**{k: v for k, v in kwargs.items() if k != "request"})
            _merge_shared(request, result)

        wrapper = sync_wrapper

    if not has_request:
        params = list(sig.parameters.values())
        request_param = inspect.Parameter(
            "request",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request,
        )
        params.insert(0, request_param)
        wrapper.__signature__ = sig.replace(parameters=params)

    return wrapper
