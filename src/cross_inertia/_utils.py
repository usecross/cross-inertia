"""Shared utility functions for Inertia.js adapters."""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any

from ._props import optional, always, defer, once


_OMITTED = object()
logger = logging.getLogger(__name__)


def _is_optional_prop(value: Any) -> bool:
    """Check if a value is an optional prop (excluded on initial load)."""
    return isinstance(value, optional)


def _is_always_prop(value: Any) -> bool:
    """Check if a value is an always prop (included even on partial reloads)."""
    return isinstance(value, always)


def _is_deferred_prop(value: Any) -> bool:
    """Check if a value is a deferred prop (loaded after initial render)."""
    return isinstance(value, defer)


def _is_once_prop(value: Any) -> bool:
    """Check if a value is a once prop (remembered by the client)."""
    return isinstance(value, once)


def _is_callable_prop(value: Any) -> bool:
    """Check if a value is a callable prop (function/lambda, not a class or special prop)."""
    return (
        callable(value)
        and not inspect.isclass(value)
        and not _is_optional_prop(value)
        and not _is_always_prop(value)
        and not _is_deferred_prop(value)
        and not _is_once_prop(value)
    )


async def _resolve_callable(value: Any) -> Any:
    """Resolve a callable value, handling both sync and async callables.

    Works with both special props (optional, always, defer, once) and regular
    callables. Special props have a __call__ method that invokes their callback.
    """
    result = value()
    if inspect.iscoroutine(result):
        return await result
    return result


async def _resolve_props(
    props: dict[str, Any],
    *,
    path_prefix: str = "",
    rescued_props: list[str] | None = None,
) -> dict[str, Any]:
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
        path = f"{path_prefix}.{key}" if path_prefix else key
        resolved_value = await _resolve_value(
            value,
            path=path,
            rescued_props=rescued_props,
        )
        if resolved_value is not _OMITTED:
            resolved[key] = resolved_value

    return resolved


async def _resolve_value(
    value: Any,
    *,
    path: str,
    rescued_props: list[str] | None,
) -> Any:
    """Resolve a single value, which may be callable, optional, always, defer, dict, or list."""
    if _is_optional_prop(value):
        if (
            not value.args
            and not value.kwargs
            and isinstance(value.callback, (optional, always, defer, once))
        ):
            return await _resolve_value(
                value.callback,
                path=path,
                rescued_props=rescued_props,
            )
        return await _resolve_callable(value)
    elif _is_always_prop(value):
        if (
            not value.args
            and not value.kwargs
            and isinstance(value.value_or_callback, (optional, always, defer, once))
        ):
            return await _resolve_value(
                value.value_or_callback,
                path=path,
                rescued_props=rescued_props,
            )
        return await _resolve_callable(value)
    elif _is_deferred_prop(value):
        try:
            if (
                not value.args
                and not value.kwargs
                and isinstance(value.callback, (optional, always, defer, once))
            ):
                return await _resolve_value(
                    value.callback,
                    path=path,
                    rescued_props=rescued_props,
                )
            return await _resolve_callable(value)
        except Exception:
            if not value.rescue:
                raise
            logger.exception("Rescued deferred Inertia prop %r", path)
            if rescued_props is not None:
                rescued_props.append(path)
            return _OMITTED
    elif _is_once_prop(value):
        if isinstance(value.value_or_callback, (optional, always, defer, once)):
            return await _resolve_value(
                value.value_or_callback,
                path=path,
                rescued_props=rescued_props,
            )
        return await _resolve_callable(value)
    elif _is_callable_prop(value):
        return await _resolve_callable(value)
    elif isinstance(value, dict):
        return await _resolve_props(
            value,
            path_prefix=path,
            rescued_props=rescued_props,
        )
    elif isinstance(value, list):
        resolved_items = []
        for index, item in enumerate(value):
            resolved_item = await _resolve_value(
                item,
                path=f"{path}.{index}",
                rescued_props=rescued_props,
            )
            if resolved_item is not _OMITTED:
                resolved_items.append(resolved_item)
        return resolved_items
    else:
        return value


def _resolve_props_sync(props: dict[str, Any]) -> dict[str, Any]:
    """
    Synchronous wrapper for resolving callable props.
    Uses asyncio.run() to execute the async resolution.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        has_running_loop = False
    else:
        has_running_loop = True

    if not has_running_loop:
        return asyncio.run(_resolve_props(props))

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, _resolve_props(props))
        return future.result()


def _resolve_props_sync_with_rescues(
    props: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Resolve props and collect deferred prop paths rescued after failures."""

    rescued_props: list[str] = []
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        has_running_loop = False
    else:
        has_running_loop = True

    if not has_running_loop:
        resolved_props = asyncio.run(_resolve_props(props, rescued_props=rescued_props))
    else:
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                _resolve_props(props, rescued_props=rescued_props),
            )
            resolved_props = future.result()

    return resolved_props, rescued_props
