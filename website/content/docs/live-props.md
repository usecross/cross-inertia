---
title: Live Props
description: Refresh props when the server broadcasts an event, with Inertia v3 live props.
order: 13
section: Advanced
---

## Overview

`live()` marks a prop that the client keeps up to date while the page is open. The page lists the channels and events the prop listens for. When one of those events is broadcast, Inertia either writes the new value the event carries or reloads the prop with a throttled partial reload.

Live props need two things besides the prop itself:

- **A broadcaster on the server.** cross-inertia publishes over the Pusher HTTP API, which [Pusher](https://pusher.com), [Laravel Reverb](https://reverb.laravel.com) and [Soketi](https://soketi.app) all speak.
- **A transport on the client.** Use Inertia's own `pusher` transport from `@inertiajs/core/pusher`, with [pusher-js](https://github.com/pusher/pusher-js).

## Basic Usage

Wrap a value or callable with `live()`, and name the channel and the events that refresh it:

```python
from cross_inertia import Channel, live
from cross_inertia.django import render

def order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "Orders/Show", {
        "order": live(
            lambda: order_data(order),
            Channel.private(f"orders.{order.id}"),
            "OrderShipped",
            "OrderCancelled",
        ),
    })
```

`live()` wraps anything a prop can be: a value, a callable, or another wrapper such as `optional()` or `defer()`. Every response lists every live prop in `liveProps`, including partial reloads, so the client's subscriptions survive them.

### Channels

```python
Channel.public("feed")            # anyone may listen
Channel.private("orders.1")       # the server authorizes each subscription
Channel.presence("room.1")        # private, with a member list
Channel.encrypted("vault.1")      # private, with end-to-end encrypted payloads
```

A string is a private channel. To listen on more channels, chain `.on()`:

```python
live(get_feed, Channel.public("feed"), "Posted").on(
    Channel.private(f"users.{user.id}"), "Mentioned"
)
```

### Throttling

`throttle=` sets the minimum number of milliseconds between reloads of a prop:

```python
live(get_stats, Channel.public("stats"), "Updated", throttle=2000)
```

## Broadcasting

Configure the broadcaster in Django settings:

```python
CROSS_INERTIA = {
    # ...
    "BROADCASTING": {
        "APP_ID": os.environ["REVERB_APP_ID"],
        "KEY": os.environ["REVERB_APP_KEY"],
        "SECRET": os.environ["REVERB_APP_SECRET"],
        "HOST": os.environ["REVERB_HOST"],
        "PORT": 443,
        "SCHEME": "https",
    },
}
```

Then broadcast when something changes:

```python
from cross_inertia.django.broadcasting import broadcast

broadcast(Channel.private(f"orders.{order.id}"), "OrderShipped", request=request)
```

The client reloads the props that listen for that event. To spare that reload, send the new values with the event:

```python
broadcast(
    Channel.private(f"orders.{order.id}"),
    "OrderShipped",
    props={"order": order_data(order)},
    request=request,
)
```

Only props that listen for that event on that channel are written. With `request=`, the tab that made the change is left out: Inertia sends the tab's connection as the `X-Socket-Id` header, and the broadcaster excludes it.

`abroadcast()` is the async version. Outside Django, use `cross_inertia.broadcasting.PusherBroadcaster` directly; `envelope()` builds an event's payload.

## Authorizing Channels

pusher-js asks your server before it subscribes to a private or presence channel. Add an endpoint with `channel_auth_view()`:

```python
from cross_inertia.django.broadcasting import channel_auth_view

def can_listen(request, channel):
    if not request.user.is_authenticated:
        return False
    if channel.name.startswith("orders."):
        order_id = channel.name.removeprefix("orders.")
        return Order.objects.filter(id=order_id, owner=request.user).exists()
    return False

urlpatterns = [
    path("broadcasting/auth", channel_auth_view(can_listen)),
]
```

For a presence channel, return the member's data (`{"user_id": ..., "user_info": {...}}`) instead of `True`.

## Client Setup

```tsx
import { createInertiaApp } from "@inertiajs/react";
import { pusher } from "@inertiajs/core/pusher";
import Pusher from "pusher-js";

const client = new Pusher(import.meta.env.VITE_REVERB_APP_KEY, {
  wsHost: import.meta.env.VITE_REVERB_HOST,
  wsPort: 443,
  wssPort: 443,
  forceTLS: true,
  enabledTransports: ["ws", "wss"],
  cluster: "",
  channelAuthorization: {
    endpoint: "/broadcasting/auth",
    transport: "ajax",
    headers: { "X-CSRFToken": csrfToken() },
  },
});

createInertiaApp({
  live: pusher({ client }),
  // ...
});
```

When a dropped connection returns, Inertia reloads every live prop once, so the page catches up on anything it missed.
