"""Sync callables resolve in the calling thread, outside any event loop.

Code that refuses to run inside an event loop (Django's ORM raises
SynchronousOnlyOperation there) must work in every kind of callable prop.
"""

import asyncio
import contextvars
import sys
import threading
from unittest.mock import patch

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


def test_async_callables_share_one_event_loop_per_resolution():
    async def start():
        state["task"] = asyncio.create_task(asyncio.sleep(0, result="awaited"))
        return "started"

    async def finish():
        return await state["task"]

    props = {"start": start, "between": where, "finish": defer(finish)}

    state: dict = {}
    resolved, _ = _resolve_props_sync_with_rescues(props)
    assert resolved == {"start": "started", "between": HERE, "finish": "awaited"}

    async def main():
        return _resolve_props_sync_with_rescues(props)[0]

    state = {}
    resolved = asyncio.run(main())
    assert resolved["finish"] == "awaited"
    assert resolved["between"]["loop"] is True  # Sync props stay inline.


REQUEST_STATE: contextvars.ContextVar[str] = contextvars.ContextVar(
    "REQUEST_STATE", default="unset"
)


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="Tasks take a shared context from 3.11"
)
@pytest.mark.parametrize("running_loop", [False, True], ids=["no-loop", "in-loop"])
def test_props_share_one_context_that_does_not_leak(running_loop):
    def set_in_sync():
        REQUEST_STATE.set("sync")
        return "set"

    async def read_then_set_in_async():
        seen = REQUEST_STATE.get()
        REQUEST_STATE.set("async")
        return seen

    props = {
        "a": set_in_sync,
        "b": read_then_set_in_async,
        "c": REQUEST_STATE.get,
        "d": defer(read_then_set_in_async),
    }

    async def in_loop():
        resolved = _resolve_props_sync_with_rescues(props)[0]
        # asyncio.run gives this task its own context, so check it here too.
        assert REQUEST_STATE.get() == "unset"
        return resolved

    if running_loop:
        resolved = asyncio.run(in_loop())
    else:
        resolved = _resolve_props_sync_with_rescues(props)[0]
    assert resolved == {"a": "set", "b": "sync", "c": "async", "d": "async"}
    assert REQUEST_STATE.get() == "unset"


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


def test_sync_resolution_inside_a_running_loop_starts_no_thread():
    # Runtimes without threads, such as Pyodide, render sync props this way.
    async def main():
        with patch.object(threading.Thread, "start", side_effect=AssertionError):
            resolved, _ = _resolve_props_sync_with_rescues(
                {"value": lambda: "x", "plain": 1, "deferred": defer(lambda: "y")}
            )
        return resolved

    assert asyncio.run(main()) == {"value": "x", "plain": 1, "deferred": "y"}


def test_async_api_is_unchanged():
    async def value():
        return "async"

    assert asyncio.run(_resolve_props({"a": value, "b": lambda: "sync"})) == {
        "a": "async",
        "b": "sync",
    }
