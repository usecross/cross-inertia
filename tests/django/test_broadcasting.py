"""Django helpers for broadcasting live prop events."""

import json

import httpx
import pytest
from django.test import RequestFactory, override_settings

from cross_inertia import Channel
from cross_inertia.broadcasting import PusherBroadcaster
from cross_inertia.django import broadcasting

CONFIG = {
    "APP_ID": "1",
    "KEY": "key",
    "SECRET": "secret",
    "HOST": "ws.example.com",
}


@pytest.fixture
def sent(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={})

    broadcaster = PusherBroadcaster(
        app_id="1",
        key="key",
        secret="secret",
        host="ws.example.com",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    monkeypatch.setattr(broadcasting, "get_broadcaster", lambda: broadcaster)
    return requests


def test_settings_configure_the_broadcaster():
    broadcasting.get_broadcaster.cache_clear()
    with override_settings(CROSS_INERTIA={"BROADCASTING": CONFIG}):
        broadcaster = broadcasting.get_broadcaster()
    broadcasting.get_broadcaster.cache_clear()
    assert broadcaster.base_url == "https://ws.example.com:443"
    assert broadcaster.key == "key"


def test_missing_settings_are_reported():
    from django.core.exceptions import ImproperlyConfigured

    broadcasting.get_broadcaster.cache_clear()
    with override_settings(CROSS_INERTIA={}), pytest.raises(ImproperlyConfigured):
        broadcasting.get_broadcaster()
    broadcasting.get_broadcaster.cache_clear()


def test_broadcast_leaves_out_the_requesting_tab(sent):
    request = RequestFactory().post("/", HTTP_X_SOCKET_ID="12.34")
    broadcasting.broadcast(
        Channel.private("orders.1"), "Shipped", props={"order": 1}, request=request
    )
    body = json.loads(sent[0].content)
    assert body["socket_id"] == "12.34"
    assert body["channels"] == ["private-orders.1"]
    assert json.loads(body["data"]) == {"__inertia": {"props": {"order": 1}}}


def auth(view, **data):
    return view(RequestFactory().post("/broadcasting/auth", data))


def test_channel_auth_signs_allowed_private_channels(sent):
    seen = []

    def can_listen(request, channel):
        seen.append(channel)
        return channel.name == "orders.1"

    view = broadcasting.channel_auth_view(can_listen)
    response = auth(view, socket_id="1.1", channel_name="private-orders.1")
    assert response.status_code == 200
    assert json.loads(response.content)["auth"].startswith("key:")
    assert seen == [Channel.private("orders.1")]
    assert (
        auth(view, socket_id="1.1", channel_name="private-orders.2").status_code == 403
    )
    assert auth(view, socket_id="1.1", channel_name="feed").status_code == 400
    assert auth(view, channel_name="private-orders.1").status_code == 400


def test_channel_auth_needs_member_data_for_presence(sent):
    member = {"user_id": 7}
    view = broadcasting.channel_auth_view(lambda request, channel: member)
    data = json.loads(auth(view, socket_id="1.1", channel_name="presence-room").content)
    assert data["channel_data"] == '{"user_id":7}'
    view = broadcasting.channel_auth_view(lambda request, channel: True)
    assert auth(view, socket_id="1.1", channel_name="presence-room").status_code == 403


def test_channel_auth_is_post_only(sent):
    view = broadcasting.channel_auth_view(lambda request, channel: True)
    assert view(RequestFactory().get("/broadcasting/auth")).status_code == 405
