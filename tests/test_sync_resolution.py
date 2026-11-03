"""Sync callables resolve in the calling thread, outside any event loop.

Code that refuses to run inside an event loop (Django's ORM raises
SynchronousOnlyOperation there) must work in every kind of callable prop.
"""

import asyncio
import threading

import pytest

from cross_inertia import always, defer, once, optional
from cross_inertia._utils import _resolve_props, _resolve_props_sync_with_rescues


def where() -> dict:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = False
    else:
        loop = True
    return {"loop": loop, "thread": threading.get_ident()}


HERE = {"loop": False, "thread": threading.get_ident()}


@pytest.mark.parametrize(
    "prop",
    [
        where,
        optional(where),
        always(where),
        defer(where),
        once(where),
        optional(defer(where)),
    ],
    ids=["callable", "optional", "always", "defer", "once", "optional-defer"],
)
def test_sync_callables_run_here_without_an_event_loop(prop):
    resolved, rescued = _resolve_props_sync_with_rescues({"value": prop})
    assert resolved == {"value": HERE}
    assert rescued == []


def test_nested_and_listed_callables_too():
    resolved, _ = _resolve_props_sync_with_rescues(
        {"nested": {"value": where}, "items": [where, {"value": where}]}
    )
    assert resolved == {
        "nested": {"value": HERE},
        "items": [HERE, {"value": HERE}],
    }


def test_async_callables_still_resolve():
    async def value():
        await asyncio.sleep(0)
        return "async"

    resolved, _ = _resolve_props_sync_with_rescues(
        {"plain": value, "deferred": defer(value)}
    )
    assert resolved == {"plain": "async", "deferred": "async"}


def test_rescued_deferred_props_are_left_out():
    def broken():
        raise RuntimeError("boom")

    resolved, rescued = _resolve_props_sync_with_rescues(
        {"ok": defer(where), "broken": defer(broken, rescue=True)}
    )
    assert resolved == {"ok": HERE}
    assert rescued == ["broken"]


def test_unrescued_errors_propagate():
    def broken():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        _resolve_props_sync_with_rescues({"broken": broken})


def test_sync_resolution_inside_a_running_loop_still_works():
    async def main():
        resolved, _ = _resolve_props_sync_with_rescues({"value": lambda: "x"})
        return resolved

    assert asyncio.run(main()) == {"value": "x"}


def test_async_api_is_unchanged():
    async def value():
        return "async"

    assert asyncio.run(_resolve_props({"a": value, "b": lambda: "sync"})) == {
        "a": "async",
        "b": "sync",
    }
