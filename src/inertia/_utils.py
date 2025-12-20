"""Shared utility functions for Inertia.js adapters."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

from ._props import optional, always, defer


def _is_optional_prop(value: Any) -> bool:
    """Check if a value is an optional prop (excluded on initial load)."""
    return isinstance(value, optional)


def _is_always_prop(value: Any) -> bool:
    """Check if a value is an always prop (included even on partial reloads)."""
    return isinstance(value, always)


def _is_deferred_prop(value: Any) -> bool:
    """Check if a value is a deferred prop (loaded after initial render)."""
    return isinstance(value, defer)


# Keep old function name for internal compatibility
def _is_lazy_prop(value: Any) -> bool:
    """Check if a value is an optional/lazy prop."""
    return _is_optional_prop(value)


def _is_callable_prop(value: Any) -> bool:
    """Check if a value is a callable prop (function/lambda, not a class or special prop)."""
    return (
        callable(value)
        and not inspect.isclass(value)
        and not _is_optional_prop(value)
        and not _is_always_prop(value)
        and not _is_deferred_prop(value)
    )


async def _resolve_callable(value: Any) -> Any:
    """Resolve a callable value, handling both sync and async callables.

    Works with both lazy props and regular callables. Both are invoked the same
    way - lazy props have a __call__ method that invokes their callback.
    """
    result = value()
    if inspect.iscoroutine(result):
        return await result
    return result


async def _resolve_props(props: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively resolve all callable props in a dictionary.

    Supports:
    - Top-level callable props: {"user": lambda: get_user()}
    - Nested callable props: {"data": {"user": lambda: get_user()}}
    - Lists with callable props: {"items": [lambda: get_item(1), lambda: get_item(2)]}
    - Async callables: {"user": async_get_user}

    Non-callable values are passed through unchanged.
    """
    resolved: dict[str, Any] = {}

    for key, value in props.items():
        resolved[key] = await _resolve_value(value)

    return resolved


async def _resolve_value(value: Any) -> Any:
    """Resolve a single value, which may be callable, optional, always, defer, dict, or list."""
    if _is_optional_prop(value):
        return await _resolve_callable(value)
    elif _is_always_prop(value):
        return await _resolve_callable(value)
    elif _is_deferred_prop(value):
        return await _resolve_callable(value)
    elif _is_callable_prop(value):
        return await _resolve_callable(value)
    elif isinstance(value, dict):
        return await _resolve_props(value)
    elif isinstance(value, list):
        return [await _resolve_value(item) for item in value]
    else:
        return value


def _resolve_props_sync(props: dict[str, Any]) -> dict[str, Any]:
    """
    Synchronous wrapper for resolving callable props.
    Uses asyncio.run() to execute the async resolution.
    """
    try:
        # Try to get the running loop
        asyncio.get_running_loop()
        # If we're already in an async context, we need to handle this differently
        # Create a new task in the existing loop
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _resolve_props(props))
            return future.result()
    except RuntimeError:
        # No running loop, we can use asyncio.run directly
        return asyncio.run(_resolve_props(props))
