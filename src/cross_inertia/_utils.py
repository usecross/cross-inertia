"""Shared utility functions for Inertia.js adapters."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable, Generator
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


# Resolution is written once, as generators that yield every callable they
# need called and receive its result. Two drivers run them: the sync driver
# calls sync callables in the current thread, outside any event loop, so code
# that must not run inside one (Django's ORM raises SynchronousOnlyOperation
# there) works in callable, optional, always, deferred and once props. Only a
# coroutine a callable returns gets an event loop. The async driver awaits as
# before.

Resolution = Generator[Callable[[], Any], Any, Any]


def _walk_props(
    props: dict[str, Any],
    *,
    path_prefix: str = "",
    rescued_props: list[str] | None = None,
) -> Resolution:
    resolved: dict[str, Any] = {}

    for key, value in props.items():
        path = f"{path_prefix}.{key}" if path_prefix else key
        resolved_value = yield from _walk_value(
            value,
            path=path,
            rescued_props=rescued_props,
        )
        if resolved_value is not _OMITTED:
            resolved[key] = resolved_value

    return resolved


def _walk_value(
    value: Any,
    *,
    path: str,
    rescued_props: list[str] | None,
) -> Resolution:
    """Resolve a single value, which may be callable, optional, always, defer, dict, or list."""
    if _is_optional_prop(value):
        if (
            not value.args
            and not value.kwargs
            and isinstance(value.callback, (optional, always, defer, once))
        ):
            return (
                yield from _walk_value(
                    value.callback,
                    path=path,
                    rescued_props=rescued_props,
                )
            )
        return (yield value)
    elif _is_always_prop(value):
        if (
            not value.args
            and not value.kwargs
            and isinstance(value.value_or_callback, (optional, always, defer, once))
        ):
            return (
                yield from _walk_value(
                    value.value_or_callback,
                    path=path,
                    rescued_props=rescued_props,
                )
            )
        return (yield value)
    elif _is_deferred_prop(value):
        try:
            if (
                not value.args
                and not value.kwargs
                and isinstance(value.callback, (optional, always, defer, once))
            ):
                return (
                    yield from _walk_value(
                        value.callback,
                        path=path,
                        rescued_props=rescued_props,
                    )
                )
            return (yield value)
        except Exception:
            if not value.rescue:
                raise
            logger.exception("Rescued deferred Inertia prop %r", path)
            if rescued_props is not None:
                rescued_props.append(path)
            return _OMITTED
    elif _is_once_prop(value):
        if isinstance(value.value_or_callback, (optional, always, defer, once)):
            return (
                yield from _walk_value(
                    value.value_or_callback,
                    path=path,
                    rescued_props=rescued_props,
                )
            )
        return (yield value)
    elif _is_callable_prop(value):
        return (yield value)
    elif isinstance(value, dict):
        return (
            yield from _walk_props(
                value,
                path_prefix=path,
                rescued_props=rescued_props,
            )
        )
    elif isinstance(value, list):
        resolved_items = []
        for index, item in enumerate(value):
            resolved_item = yield from _walk_value(
                item,
                path=f"{path}.{index}",
                rescued_props=rescued_props,
            )
            if resolved_item is not _OMITTED:
                resolved_items.append(resolved_item)
        return resolved_items
    else:
        return value


def _run_coroutine(coroutine: Any) -> Any:
    """Run a coroutine to completion from sync code, in a fresh event loop
    (on another thread when this one already runs a loop)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(asyncio.run, coroutine).result()


def _drive_sync(resolution: Resolution) -> Any:
    try:
        request = next(resolution)
        while True:
            try:
                result = request()
                if inspect.iscoroutine(result):
                    result = _run_coroutine(result)
            except Exception as error:
                request = resolution.throw(error)
            else:
                request = resolution.send(result)
    except StopIteration as stop:
        return stop.value


async def _drive_async(resolution: Resolution) -> Any:
    try:
        request = next(resolution)
        while True:
            try:
                result = request()
                if inspect.iscoroutine(result):
                    result = await result
            except Exception as error:
                request = resolution.throw(error)
            else:
                request = resolution.send(result)
    except StopIteration as stop:
        return stop.value


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
    return await _drive_async(
        _walk_props(props, path_prefix=path_prefix, rescued_props=rescued_props)
    )


async def _resolve_value(
    value: Any,
    *,
    path: str,
    rescued_props: list[str] | None,
) -> Any:
    """Resolve a single value, which may be callable, optional, always, defer, dict, or list."""
    return await _drive_async(
        _walk_value(value, path=path, rescued_props=rescued_props)
    )


def _resolve_props_sync(props: dict[str, Any]) -> dict[str, Any]:
    """
    Resolve callable props synchronously: sync callables run in the calling
    thread, outside any event loop; async ones get a fresh loop.
    """
    return _drive_sync(_walk_props(props))


def _resolve_props_sync_with_rescues(
    props: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Resolve props and collect deferred prop paths rescued after failures."""

    rescued_props: list[str] = []
    resolved_props = _drive_sync(_walk_props(props, rescued_props=rescued_props))
    return resolved_props, rescued_props
