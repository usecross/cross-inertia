"""Tests for live props functionality."""

import pytest
from cross_inertia import live, broadcast_props
from cross_inertia._page import (
    PageRequestContext,
    PageRenderOptions,
    build_inertia_page,
)


class MockAdapter:
    """Mock adapter for testing."""

    def __init__(self, headers=None, method="GET", url="/test"):
        self._headers = headers or {}
        self._method = method
        self._url = url

    @property
    def headers(self):
        return self._headers

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url


def test_live_prop_basic():
    """Test basic live prop creation and invocation."""
    def get_order():
        return {"id": 1, "status": "shipped"}

    prop = live(
        get_order,
        on="order.updated",
        channel={"name": "orders.1", "type": "private"}
    )

    assert callable(prop)
    assert prop() == {"id": 1, "status": "shipped"}
    assert prop.on == ["order.updated"]
    assert prop.channel == [{"name": "orders.1", "type": "private"}]
    assert prop.throttle is None


def test_live_prop_with_args():
    """Test live prop with arguments."""
    def get_order(order_id, include_items=False):
        result = {"id": order_id, "status": "shipped"}
        if include_items:
            result["items"] = []
        return result

    prop = live(
        get_order,
        42,
        include_items=True,
        on="order.updated",
        channel={"name": "orders.42", "type": "private"}
    )

    assert prop() == {"id": 42, "status": "shipped", "items": []}


def test_live_prop_multiple_events():
    """Test live prop listening to multiple events."""
    def get_order():
        return {"id": 1}

    prop = live(
        get_order,
        on=["order.updated", "order.cancelled"],
        channel={"name": "orders.1", "type": "private"}
    )

    assert prop.on == ["order.updated", "order.cancelled"]


def test_live_prop_multiple_channels():
    """Test live prop listening on multiple channels."""
    def get_metrics():
        return {"total": 100}

    prop = live(
        get_metrics,
        on="metrics.updated",
        channel=[
            {"name": "dashboard", "type": "private"},
            {"name": "metrics", "type": "public"}
        ]
    )

    assert len(prop.channel) == 2


def test_live_prop_with_throttle():
    """Test live prop with custom throttle."""
    def get_count():
        return 5

    prop = live(
        get_count,
        on="count.changed",
        channel={"name": "counter", "type": "public"},
        throttle=5000
    )

    assert prop.throttle == 5000


def test_live_prop_requires_callable():
    """Test that live() requires a callable."""
    with pytest.raises(ValueError, match="live\\(\\) requires a callable"):
        live("not a callable", on="test.event")


def test_live_prop_in_page_metadata():
    """Test that live props appear in page metadata."""
    def get_order():
        return {"id": 1, "status": "shipped"}

    adapter = MockAdapter(headers={"X-Inertia": "true"})
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/orders/1",
        page_url="/orders/1",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/orders/1",
    )

    options = PageRenderOptions(
        component="Orders/Show",
        props={
            "order": live(
                get_order,
                on="order.updated",
                channel={"name": "orders.1", "type": "private"}
            )
        },
    )

    result = build_inertia_page(context, options)

    assert result.page_data is not None
    assert "liveProps" in result.page_data
    assert "order" in result.page_data["liveProps"]

    live_metadata = result.page_data["liveProps"]["order"]
    assert "listeners" in live_metadata
    assert len(live_metadata["listeners"]) == 1

    listener = live_metadata["listeners"][0]
    assert listener["channel"] == {"name": "orders.1", "type": "private"}
    assert listener["events"] == ["order.updated"]


def test_live_prop_with_multiple_events_metadata():
    """Test live prop metadata with multiple events."""
    def get_order():
        return {"id": 1}

    adapter = MockAdapter()
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/orders/1",
        page_url="/orders/1",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/orders/1",
    )

    options = PageRenderOptions(
        component="Orders/Show",
        props={
            "order": live(
                get_order,
                on=["order.updated", "order.cancelled"],
                channel={"name": "orders.1", "type": "private"}
            )
        },
    )

    result = build_inertia_page(context, options)

    listener = result.page_data["liveProps"]["order"]["listeners"][0]
    assert set(listener["events"]) == {"order.updated", "order.cancelled"}


def test_live_prop_with_throttle_metadata():
    """Test that throttle appears in metadata."""
    def get_metrics():
        return {"total": 100}

    adapter = MockAdapter()
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/dashboard",
        page_url="/dashboard",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/dashboard",
    )

    options = PageRenderOptions(
        component="Dashboard",
        props={
            "metrics": live(
                get_metrics,
                on="metrics.updated",
                channel={"name": "dashboard", "type": "private"},
                throttle=2000
            )
        },
    )

    result = build_inertia_page(context, options)

    assert result.page_data["liveProps"]["metrics"]["throttle"] == 2000


def test_live_prop_resolves_value():
    """Test that live prop values are resolved in props."""
    def get_order():
        return {"id": 1, "status": "shipped"}

    adapter = MockAdapter()
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/orders/1",
        page_url="/orders/1",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/orders/1",
    )

    options = PageRenderOptions(
        component="Orders/Show",
        props={
            "order": live(
                get_order,
                on="order.updated",
                channel={"name": "orders.1", "type": "private"}
            )
        },
    )

    result = build_inertia_page(context, options)

    assert result.page_data["props"]["order"] == {"id": 1, "status": "shipped"}


def test_live_prop_in_partial_reload():
    """Test live prop behavior during partial reloads."""
    def get_order():
        return {"id": 1, "status": "shipped"}

    adapter = MockAdapter(headers={
        "X-Inertia": "true",
        "X-Inertia-Partial-Component": "Orders/Show",
        "X-Inertia-Partial-Data": "order"
    })
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/orders/1",
        page_url="/orders/1",
        shared_data={},
        asset_version="abc123",
        is_inertia=True,
        is_prefetch=False,
        partial_component="Orders/Show",
        partial_only=["order"],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/orders/1",
    )

    options = PageRenderOptions(
        component="Orders/Show",
        props={
            "order": live(
                get_order,
                on="order.updated",
                channel={"name": "orders.1", "type": "private"}
            ),
            "other": "value"
        },
    )

    result = build_inertia_page(context, options)

    assert "order" in result.page_data["props"]
    assert "other" not in result.page_data["props"]
    assert "order" in result.page_data["liveProps"]


def test_broadcast_props_structure():
    """Test broadcast_props helper returns correct structure."""
    props = {
        "order": {"id": 1, "status": "shipped"},
        "user.name": "John Doe"
    }

    result = broadcast_props(props)

    assert "__inertia" in result
    assert "props" in result["__inertia"]
    assert result["__inertia"]["props"] == props


def test_broadcast_props_empty():
    """Test broadcast_props with empty props."""
    result = broadcast_props({})

    assert "__inertia" in result
    assert result["__inertia"]["props"] == {}


def test_live_prop_no_channels():
    """Test live prop without explicit channels."""
    def get_data():
        return {"value": 42}

    prop = live(
        get_data,
        on="data.changed"
    )

    assert prop.on == ["data.changed"]
    assert prop.channel == []


def test_live_prop_no_channels_metadata():
    """Test live prop metadata without channels."""
    def get_data():
        return {"value": 42}

    adapter = MockAdapter()
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/test",
        page_url="/test",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/test",
    )

    options = PageRenderOptions(
        component="Test",
        props={
            "data": live(get_data, on="data.changed")
        },
    )

    result = build_inertia_page(context, options)

    listener = result.page_data["liveProps"]["data"]["listeners"][0]
    assert "channel" not in listener
    assert listener["events"] == ["data.changed"]


def test_live_prop_multiple_channels_metadata():
    """Test live prop metadata with multiple channels."""
    def get_metrics():
        return {"total": 100}

    adapter = MockAdapter()
    context = PageRequestContext(
        method="GET",
        headers=adapter.headers,
        current_url="/dashboard",
        page_url="/dashboard",
        shared_data={},
        asset_version="abc123",
        is_inertia=False,
        is_prefetch=False,
        partial_component=None,
        partial_only=[],
        partial_except=[],
        reset_props=[],
        except_once_props=set(),
        error_bag=None,
        version_conflict_location="/dashboard",
    )

    options = PageRenderOptions(
        component="Dashboard",
        props={
            "metrics": live(
                get_metrics,
                on="metrics.updated",
                channel=[
                    {"name": "dashboard", "type": "private"},
                    {"name": "metrics", "type": "public"}
                ]
            )
        },
    )

    result = build_inertia_page(context, options)

    listeners = result.page_data["liveProps"]["metrics"]["listeners"]
    assert len(listeners) == 2
    assert listeners[0]["channel"] == {"name": "dashboard", "type": "private"}
    assert listeners[1]["channel"] == {"name": "metrics", "type": "public"}
