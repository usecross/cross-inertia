"""Broadcasting events for live props.

A live prop (`cross_inertia.live`) makes the client listen for events on
channels. This module publishes those events. `envelope()` builds an event's
payload in the shape Inertia reads, and `PusherBroadcaster` publishes it over
the Pusher HTTP API, which Pusher, Laravel Reverb and Soketi all speak. On the
client, Inertia's own `pusher` transport (`@inertiajs/core/pusher`) subscribes.

Example:
    from cross_inertia import Channel
    from cross_inertia.broadcasting import PusherBroadcaster

    broadcaster = PusherBroadcaster(
        app_id="1", key="app-key", secret="app-secret",
        host="ws.example.com", port=443, scheme="https",
    )
    channel = Channel.private(f"orders.{order.id}")

    # The client reloads the props that listen for this event.
    broadcaster.broadcast(channel, "OrderShipped")

    # Or deliver the new value, which spares that reload.
    broadcaster.broadcast(channel, "OrderShipped", props={"order": order_data(order)})
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlencode

import httpx

from ._props import Channel

# The prefixes Pusher-protocol servers use for channel types; the client's
# transport applies the same ones.
CHANNEL_PREFIXES = {
    "public": "",
    "private": "private-",
    "presence": "presence-",
    "encrypted-private": "private-encrypted-",
}


def channel_name(channel: Channel | str) -> str:
    """The broadcaster's name for a channel (with its type's prefix)."""
    if isinstance(channel, str):
        return channel
    return f"{CHANNEL_PREFIXES.get(channel.type, '')}{channel.name}"


def parse_channel_name(name: str) -> Channel:
    """The channel a broadcaster's prefixed name refers to."""
    for type_, prefix in sorted(
        CHANNEL_PREFIXES.items(), key=lambda item: len(item[1]), reverse=True
    ):
        if prefix and name.startswith(prefix):
            return Channel(name[len(prefix) :], type_)
    return Channel(name, "public")


def envelope(
    event: str | None = None,
    *,
    props: dict[str, Any] | None = None,
    socket_id: str | None = None,
) -> dict[str, Any]:
    """An event payload for live props.

    Args:
        event: The event name, for transports that cannot route by name
            (such as Action Cable); Pusher routes by the event it is sent as.
        props: New values for live props, by prop path. The client writes
            them instead of reloading those props. Only props that listen for
            this event on this channel are written.
        socket_id: The connection that caused the change: that client ignores
            the event (for broadcasters that cannot exclude a connection).
    """
    inertia: dict[str, Any] = {}
    if event is not None:
        inertia["event"] = event
    if props is not None:
        inertia["props"] = props
    if socket_id is not None:
        inertia["socketId"] = socket_id
    return {"__inertia": inertia}


class BroadcastError(Exception):
    """The broadcaster refused or could not be reached."""


class PusherBroadcaster:
    """Publishes events over the Pusher HTTP API (Pusher, Reverb, Soketi).

    Args:
        app_id, key, secret: The app's credentials.
        host: The API host (for Pusher itself, `api-<cluster>.pusher.com`).
        port, scheme: Where the API listens.
        timeout: Seconds to wait for each publish.
    """

    def __init__(
        self,
        *,
        app_id: str,
        key: str,
        secret: str,
        host: str,
        port: int = 443,
        scheme: str = "https",
        timeout: float = 5.0,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self.app_id = str(app_id)
        self.key = key
        self.secret = secret
        self.base_url = f"{scheme}://{host}:{port}"
        self.timeout = timeout
        self._client = client
        self._async_client = async_client

    # Publishing.

    def _request(
        self,
        channels: Iterable[Channel | str],
        event: str,
        payload: Any,
        socket_id: str | None,
    ) -> tuple[str, bytes]:
        names = [channel_name(channel) for channel in channels]
        if not names:
            raise ValueError("Broadcast to at least one channel")
        body: dict[str, Any] = {
            "name": event,
            "channels": names,
            "data": json.dumps(payload, separators=(",", ":")),
        }
        if socket_id:
            body["socket_id"] = socket_id
        content = json.dumps(body, separators=(",", ":")).encode()
        path = f"/apps/{self.app_id}/events"
        return (
            f"{self.base_url}{path}?{self.signed_query('POST', path, content)}",
            content,
        )

    def signed_query(
        self, method: str, path: str, body: bytes = b"", timestamp: int | None = None
    ) -> str:
        """The authentication query string for a Pusher HTTP API request."""
        params: dict[str, str] = {
            "auth_key": self.key,
            "auth_timestamp": str(int(time.time()) if timestamp is None else timestamp),
            "auth_version": "1.0",
        }
        if body:
            params["body_md5"] = hashlib.md5(body).hexdigest()
        query = "&".join(f"{name}={params[name]}" for name in sorted(params))
        signature = hmac.new(
            self.secret.encode(), f"{method}\n{path}\n{query}".encode(), hashlib.sha256
        ).hexdigest()
        return urlencode({**params, "auth_signature": signature})

    def trigger(
        self,
        channels: Channel | str | Iterable[Channel | str],
        event: str,
        payload: Any,
        *,
        socket_id: str | None = None,
    ) -> None:
        """Publish `payload` as `event` on `channels` (excluding `socket_id`)."""
        if isinstance(channels, (Channel, str)):
            channels = [channels]
        url, content = self._request(channels, event, payload, socket_id)
        client = self._client or httpx.Client(timeout=self.timeout)
        try:
            response = client.post(
                url, content=content, headers={"Content-Type": "application/json"}
            )
        except httpx.HTTPError as error:
            raise BroadcastError(
                f"The broadcaster could not be reached: {error}"
            ) from error
        finally:
            if self._client is None:
                client.close()
        if response.status_code >= 400:
            raise BroadcastError(
                f"The broadcaster refused the event ({response.status_code}): {response.text}"
            )

    async def atrigger(
        self,
        channels: Channel | str | Iterable[Channel | str],
        event: str,
        payload: Any,
        *,
        socket_id: str | None = None,
    ) -> None:
        """`trigger`, for async code."""
        if isinstance(channels, (Channel, str)):
            channels = [channels]
        url, content = self._request(channels, event, payload, socket_id)
        client = self._async_client or httpx.AsyncClient(timeout=self.timeout)
        try:
            response = await client.post(
                url, content=content, headers={"Content-Type": "application/json"}
            )
        except httpx.HTTPError as error:
            raise BroadcastError(
                f"The broadcaster could not be reached: {error}"
            ) from error
        finally:
            if self._async_client is None:
                await client.aclose()
        if response.status_code >= 400:
            raise BroadcastError(
                f"The broadcaster refused the event ({response.status_code}): {response.text}"
            )

    def broadcast(
        self,
        channels: Channel | str | Iterable[Channel | str],
        event: str,
        *,
        props: dict[str, Any] | None = None,
        socket_id: str | None = None,
    ) -> None:
        """Tell live props listening for `event` that they changed (with their
        new values when `props` is given). `socket_id` (the X-Socket-Id header
        of the request that caused it) is left out."""
        self.trigger(channels, event, envelope(props=props), socket_id=socket_id)

    async def abroadcast(
        self,
        channels: Channel | str | Iterable[Channel | str],
        event: str,
        *,
        props: dict[str, Any] | None = None,
        socket_id: str | None = None,
    ) -> None:
        """`broadcast`, for async code."""
        await self.atrigger(channels, event, envelope(props=props), socket_id=socket_id)

    # Authorising subscriptions.

    def authorize(
        self,
        socket_id: str,
        channel: Channel | str,
        *,
        user_data: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """The answer to a client's private or presence channel auth request
        (what pusher-js expects from its auth endpoint). Only call this once
        the user may subscribe to the channel."""
        name = channel_name(channel)
        result: dict[str, str] = {}
        to_sign = f"{socket_id}:{name}"
        if user_data is not None:
            result["channel_data"] = json.dumps(user_data, separators=(",", ":"))
            to_sign = f"{to_sign}:{result['channel_data']}"
        signature = hmac.new(
            self.secret.encode(), to_sign.encode(), hashlib.sha256
        ).hexdigest()
        return {"auth": f"{self.key}:{signature}", **result}
