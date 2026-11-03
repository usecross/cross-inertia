"""Django helpers for broadcasting live prop events.

Configuration in settings.py (Pusher, Laravel Reverb or Soketi):

    CROSS_INERTIA = {
        ...
        "BROADCASTING": {
            "APP_ID": "1",
            "KEY": "app-key",
            "SECRET": "app-secret",
            "HOST": "ws.example.com",
            "PORT": 443,
            "SCHEME": "https",
        },
    }

Publishing, from a view or a background task:

    from cross_inertia import Channel
    from cross_inertia.django.broadcasting import broadcast

    broadcast(Channel.private(f"orders.{order.id}"), "OrderShipped", request=request)

Authorising private and presence channels (pusher-js posts `socket_id` and
`channel_name` to its auth endpoint):

    from cross_inertia.django.broadcasting import channel_auth_view

    def can_listen(request, channel):
        return request.user.is_authenticated and channel.name.startswith("orders.")

    urlpatterns = [path("broadcasting/auth", channel_auth_view(can_listen))]
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from .._props import Channel
from ..broadcasting import PusherBroadcaster, parse_channel_name

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

Channels = Channel | str | Iterable[Channel | str]


@lru_cache(maxsize=1)
def get_broadcaster() -> PusherBroadcaster:
    """The broadcaster configured in CROSS_INERTIA["BROADCASTING"]."""
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    config = getattr(settings, "CROSS_INERTIA", {}).get("BROADCASTING")
    if not config:
        raise ImproperlyConfigured(
            'Set CROSS_INERTIA["BROADCASTING"] to broadcast live prop events.'
        )
    try:
        return PusherBroadcaster(
            app_id=str(config["APP_ID"]),
            key=config["KEY"],
            secret=config["SECRET"],
            host=config["HOST"],
            port=int(config.get("PORT", 443)),
            scheme=config.get("SCHEME", "https"),
            timeout=float(config.get("TIMEOUT", 5.0)),
        )
    except KeyError as missing:
        raise ImproperlyConfigured(
            f'CROSS_INERTIA["BROADCASTING"] needs {missing}.'
        ) from None


def _socket_id(request: HttpRequest | None) -> str | None:
    """The X-Socket-Id Inertia sends with each visit: the change's own tab."""
    return request.headers.get("X-Socket-Id") if request is not None else None


def broadcast(
    channels: Channels,
    event: str,
    *,
    props: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> None:
    """Tell the live props listening for `event` that they changed, with their
    new values when `props` is given. With `request`, the tab that sent it is
    left out (it already has the change)."""
    get_broadcaster().broadcast(
        channels, event, props=props, socket_id=_socket_id(request)
    )


async def abroadcast(
    channels: Channels,
    event: str,
    *,
    props: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> None:
    """`broadcast`, for async code."""
    await get_broadcaster().abroadcast(
        channels, event, props=props, socket_id=_socket_id(request)
    )


Authorizer = Callable[["HttpRequest", Channel], "bool | dict[str, Any] | None"]


def channel_auth_view(authorize: Authorizer) -> Callable[[HttpRequest], HttpResponse]:
    """A view for pusher-js's channel authorization endpoint.

    `authorize(request, channel)` decides: falsy refuses (403), True allows a
    private channel, and for a presence channel it returns the member's data
    (`{"user_id": ..., "user_info": {...}}`).
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST

    @require_POST
    def view(request: HttpRequest) -> HttpResponse:
        socket_id = request.POST.get("socket_id", "")
        name = request.POST.get("channel_name", "")
        if not socket_id or not name:
            return JsonResponse(
                {"error": "socket_id and channel_name are required."}, status=400
            )
        channel = parse_channel_name(name)
        if channel.type == "public":
            return JsonResponse(
                {"error": "Public channels need no authorization."}, status=400
            )
        allowed = authorize(request, channel)
        if not allowed:
            return JsonResponse({"error": "Not allowed."}, status=403)
        user_data = (
            allowed
            if channel.type == "presence" and isinstance(allowed, dict)
            else None
        )
        if channel.type == "presence" and user_data is None:
            return JsonResponse(
                {"error": "Presence channels need the member's data."}, status=403
            )
        return JsonResponse(
            get_broadcaster().authorize(socket_id, name, user_data=user_data)
        )

    return view
