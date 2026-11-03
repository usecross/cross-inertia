"""Live props (Inertia v3): liveProps metadata, resolution and broadcasting."""

import json

import httpx
import pytest

from cross_inertia import Channel, defer, live, optional
from cross_inertia.broadcasting import (
    BroadcastError,
    PusherBroadcaster,
    channel_name,
    envelope,
    parse_channel_name,
)
from tests.test_page_builder import build_result


def page(props, partial=None):
    return build_result(
        props,
        headers={"X-Inertia": "true"} if partial else None,
        partial_component="TestComponent" if partial else None,
        partial_only=partial,
    ).page_data


ORDERS = Channel.private("orders.1")


def test_live_props_resolve_and_list_their_listeners():
    data = page(
        {
            "order": live(lambda: {"id": 1}, ORDERS, "OrderShipped", "OrderCancelled"),
            "feed": live(["a"], Channel.public("feed"), "Posted", throttle=500).on(
                "users.7", "Mentioned"
            ),
            "plain": 1,
        }
    )
    assert data["props"]["order"] == {"id": 1}
    assert data["props"]["feed"] == ["a"]
    assert data["liveProps"] == {
        "order": {
            "listeners": [
                {
                    "channel": {"name": "orders.1", "type": "private"},
                    "events": ["OrderShipped", "OrderCancelled"],
                }
            ]
        },
        "feed": {
            "listeners": [
                {"channel": {"name": "feed", "type": "public"}, "events": ["Posted"]},
                {
                    "channel": {"name": "users.7", "type": "private"},
                    "events": ["Mentioned"],
                },
            ],
            "throttle": 500,
        },
    }


def test_pages_without_live_props_have_no_live_props_key():
    assert "liveProps" not in page({"plain": 1})


def test_nested_live_props_use_dot_paths():
    data = page({"orders": {"latest": live(lambda: 3, ORDERS, "Placed")}})
    assert data["props"]["orders"] == {"latest": 3}
    assert list(data["liveProps"]) == ["orders.latest"]


def test_partial_reloads_still_list_every_live_prop():
    props = {
        "order": live(lambda: {"id": 1}, ORDERS, "OrderShipped"),
        "stats": live(lambda: 2, ORDERS, "Stats"),
    }
    data = page(props, partial=["stats"])
    assert data["props"] == {"stats": 2, "errors": {}}
    assert set(data["liveProps"]) == {"order", "stats"}


def test_live_wraps_optional_and_deferred_props():
    props = {
        "history": live(optional(lambda: ["old"]), ORDERS, "Archived"),
        "totals": live(defer(lambda: 9), ORDERS, "Totals"),
    }
    data = page(props)
    # An optional prop nobody asked for stays out, but its listeners are sent.
    assert "history" not in data["props"]
    assert "totals" not in data["props"]
    assert data["deferredProps"] == {"default": ["totals"]}
    assert set(data["liveProps"]) == {"history", "totals"}
    data = page(props, partial=["history", "totals"])
    assert data["props"]["history"] == ["old"]
    assert data["props"]["totals"] == 9


def test_live_needs_a_listener():
    with pytest.raises(ValueError):
        live(1, ORDERS)
    with pytest.raises(ValueError):
        page({"x": live(1)})


def test_listeners_on_the_same_channel_merge():
    prop = live(1, ORDERS, "A").on(Channel.private("orders.1"), "B", "A")
    assert prop.metadata()["listeners"] == [
        {"channel": {"name": "orders.1", "type": "private"}, "events": ["A", "B"]}
    ]


def test_channel_names_and_prefixes():
    assert channel_name(Channel.private("orders.1")) == "private-orders.1"
    assert channel_name(Channel.presence("room")) == "presence-room"
    assert channel_name(Channel.encrypted("vault")) == "private-encrypted-vault"
    assert channel_name(Channel.public("feed")) == "feed"
    assert parse_channel_name("private-encrypted-vault") == Channel.encrypted("vault")
    assert parse_channel_name("private-orders.1") == Channel.private("orders.1")
    assert parse_channel_name("presence-room") == Channel.presence("room")
    assert parse_channel_name("feed") == Channel.public("feed")


def test_envelope():
    assert envelope() == {"__inertia": {}}
    assert envelope("Shipped", props={"order": 1}, socket_id="1.2") == {
        "__inertia": {"event": "Shipped", "props": {"order": 1}, "socketId": "1.2"}
    }


# Pusher's documented examples (pusher.com/docs/channels/library_auth_reference).
DOCS = PusherBroadcaster(
    app_id="3",
    key="278d425bdf160c739803",
    secret="7ad3773142a6692b25b8",
    host="api.pusherapp.com",
    port=80,
    scheme="http",
)


def test_private_channel_signature_matches_pusher_docs():
    assert DOCS.authorize("1234.1234", "private-foobar") == {
        "auth": "278d425bdf160c739803:58df8b0c36d6982b82c3ecf6b4662e34fe8c25bba48f5369f135bf843651c3a4"
    }


def test_presence_channel_signature_matches_pusher_docs():
    result = DOCS.authorize(
        "1234.1234",
        Channel.presence("foobar"),
        user_data={"user_id": 10, "user_info": {"name": "Mr. Channels"}},
    )
    assert result == {
        "auth": "278d425bdf160c739803:31935e7d86dba64c2a90aed31fdc61869f9b22ba9d8863bba239c03ca481bc80",
        "channel_data": '{"user_id":10,"user_info":{"name":"Mr. Channels"}}',
    }


def test_http_api_signature_matches_pusher_docs():
    body = b'{"name":"foo","channels":["project-3"],"data":"{\\"some\\":\\"data\\"}"}'
    query = DOCS.signed_query("POST", "/apps/3/events", body, timestamp=1353088179)
    assert "body_md5=ec365a775a4cd0599faeb73354201b6f" in query
    assert query.endswith(
        "auth_signature=da454824c97ba181a32ccc17a72625ba02771f50b50e1e7430e47a1f3f457e6c"
    )


def recording_broadcaster(status=200):
    sent = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(status, json={})

    transport = httpx.MockTransport(handler)
    broadcaster = PusherBroadcaster(
        app_id="1",
        key="k",
        secret="s",
        host="ws.example.com",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )
    return broadcaster, sent


def test_broadcast_publishes_an_envelope():
    broadcaster, sent = recording_broadcaster()
    broadcaster.broadcast(
        ORDERS, "OrderShipped", props={"order": {"id": 1}}, socket_id="9.9"
    )
    (request,) = sent
    assert request.url.path == "/apps/1/events"
    assert request.url.host == "ws.example.com"
    body = json.loads(request.content)
    assert body["name"] == "OrderShipped"
    assert body["channels"] == ["private-orders.1"]
    assert body["socket_id"] == "9.9"
    assert json.loads(body["data"]) == {"__inertia": {"props": {"order": {"id": 1}}}}
    query = dict(request.url.params)
    assert set(query) == {
        "auth_key",
        "auth_timestamp",
        "auth_version",
        "body_md5",
        "auth_signature",
    }


def test_async_broadcast():
    import asyncio

    broadcaster, sent = recording_broadcaster()
    asyncio.run(broadcaster.abroadcast([ORDERS, "feed"], "Posted"))
    assert json.loads(sent[0].content)["channels"] == ["private-orders.1", "feed"]


def test_refusals_raise():
    broadcaster, _ = recording_broadcaster(status=413)
    with pytest.raises(BroadcastError, match="413"):
        broadcaster.broadcast(ORDERS, "Big", props={"x": "y"})
