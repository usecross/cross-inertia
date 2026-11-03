---
title: Live Props
description: Real-time prop updates using broadcast events.
order: 11
section: Advanced
---

## Overview

Live props automatically refresh when a broadcast event fires, keeping your UI in sync with server-side changes without polling. This is ideal for real-time features like order statuses, unread message counts, or dashboard metrics.

## Using Live Props

Wrap data with the `live` function and specify which events should trigger a refresh:

```python
from cross_inertia import live
from cross_inertia.fastapi import InertiaDep

@app.get("/orders/{order_id}")
async def show_order(order_id: int, inertia: InertiaDep):
    order = get_order(order_id)
    return inertia.render("Orders/Show", {
        "order": live(
            lambda: get_order(order_id),
            on="order.updated",
            channel={"name": f"orders.{order_id}", "type": "private"}
        ),
    })
```

When the `order.updated` event is broadcast on the `orders.{order_id}` channel, Inertia automatically makes a partial reload to fetch the latest value.

## Client-Side Setup

Configure your Inertia app to use a broadcast transport (Laravel Echo, Pusher, or Action Cable):

```tsx
import { createInertiaApp } from '@inertiajs/react'
import { echo } from '@inertiajs/react/echo'
import Echo from 'laravel-echo'
import Pusher from 'pusher-js'

// Configure Laravel Echo
window.Pusher = Pusher
window.Echo = new Echo({
  broadcaster: 'pusher',
  key: import.meta.env.VITE_PUSHER_APP_KEY,
  cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
  forceTLS: true
})

createInertiaApp({
  // ... other options
  live: echo(),  // Enable live props with Echo transport
})
```

For other transports:

```tsx
import { pusher } from '@inertiajs/react/pusher'
import { actionCable } from '@inertiajs/react/action-cable'

// Pusher directly
live: pusher(pusherClient)

// Action Cable
live: actionCable(consumer)
```

## Multiple Events

A live prop can listen for multiple events:

```python
@app.get("/orders/{order_id}")
async def show_order(order_id: int, inertia: InertiaDep):
    return inertia.render("Orders/Show", {
        "order": live(
            lambda: get_order(order_id),
            on=["order.updated", "order.cancelled"],
            channel={"name": f"orders.{order_id}", "type": "private"}
        ),
    })
```

## Channel Types

Live props support all channel types:

```python
# Public channel (no authentication required)
live(
    get_metrics,
    on="metrics.updated",
    channel={"name": "metrics", "type": "public"}
)

# Private channel (requires authentication)
live(
    get_order,
    on="order.updated",
    channel={"name": f"orders.{order_id}", "type": "private"}
)

# Presence channel (tracks who's online)
live(
    get_users_online,
    on="user.joined",
    channel={"name": "chat.room", "type": "presence"}
)

# Encrypted private channel
live(
    get_sensitive_data,
    on="data.updated",
    channel={"name": "sensitive", "type": "encrypted-private"}
)
```

## Multiple Channels

Listen on multiple channels for the same event:

```python
@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "metrics": live(
            get_metrics,
            on="metrics.updated",
            channel=[
                {"name": "dashboard", "type": "private"},
                {"name": "metrics", "type": "public"}
            ]
        ),
    })
```

## Throttling

By default, live props throttle refreshes to once per second. You can customize this:

```python
# Per-prop throttle
live(
    get_metrics,
    on="metrics.updated",
    channel={"name": "dashboard", "type": "private"},
    throttle=5000  # 5 seconds
)
```

Or set a global default in your client setup:

```tsx
createInertiaApp({
  live: echo({ throttle: 2000 }),  // 2 seconds for all live props
})
```

Manual reloads using `router.reload()` are never throttled.

## Combining with Other Prop Types

Live props work seamlessly with other prop wrappers:

```python
from cross_inertia import live, defer, once, always

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        # Deferred + live: load after page renders, then keep updated
        "metrics": defer(
            lambda: get_metrics(),
            group="default"
        ).live(
            on="metrics.updated",
            channel={"name": "dashboard", "type": "private"}
        ),
        
        # Once + live: remember across navigations, but still update
        "settings": once(
            lambda: get_settings()
        ).live(
            on="settings.changed",
            channel={"name": "user.settings", "type": "private"}
        ),
        
        # Always + live: always included, always fresh
        "notifications": always(
            lambda: get_notifications()
        ).live(
            on="notification.received",
            channel={"name": "user.notifications", "type": "private"}
        ),
    })
```

**Note:** Merge props cannot be live.

## Broadcasting Props in Events

To avoid making a server request for every listener, events can broadcast the new values directly:

```python
from cross_inertia import broadcast_props

class OrderUpdated:
    def __init__(self, order):
        self.order = order
    
    def broadcast_on(self):
        return [PrivateChannel(f"orders.{self.order.id}")]
    
    def broadcast_with(self):
        return {
            "order_id": self.order.id,
            **broadcast_props({
                "order": {
                    "id": self.order.id,
                    "status": self.order.status,
                    "total": str(self.order.total),
                }
            })
        }
```

When an event includes the `__inertia.props` key (returned by `broadcast_props`), Inertia uses those values without making a server request. This is especially important for high-traffic scenarios (e.g., a dashboard open in many tabs).

**Important:** The broadcasted values must be identical for all users on the channel. Don't broadcast user-specific data on shared channels.

## Loading State

Use the `useProp()` hook to track when a live prop is refreshing:

```tsx
import { useProp } from '@inertiajs/react'

export default function Dashboard({ metrics }: { metrics: MetricsData }) {
  const { loading } = useProp('metrics')
  
  return (
    <div>
      {loading && <div className="spinner">Updating...</div>}
      <MetricsDisplay data={metrics} />
    </div>
  )
}
```

The `loading` flag is `true` while any request (including deferred and live reloads) is refreshing the prop.

## Broadcasting Setup

Live props require a broadcasting system. Here are common setups:

### Laravel Reverb (Recommended)

For Laravel Reverb, install and configure broadcasting:

```bash
php artisan install:broadcasting
php artisan reverb:start
```

Then in your event class:

```python
# Python equivalent - implement your broadcaster
class OrderUpdated:
    def __init__(self, order):
        self.order = order
    
    def broadcast_on(self):
        return [PrivateChannel(f"orders.{self.order.id}")]
```

### Python Broadcasting

While Cross-Inertia provides the live props protocol, you'll need a Python broadcasting solution:

- **Django Channels** with Redis/WebSocket backend
- **FastAPI WebSocket** with Redis pub/sub
- **Third-party services** like Pusher, Ably, or AWS IoT

Example with Pusher in FastAPI:

```python
import pusher

pusher_client = pusher.Pusher(
    app_id=os.getenv("PUSHER_APP_ID"),
    key=os.getenv("PUSHER_KEY"),
    secret=os.getenv("PUSHER_SECRET"),
    cluster=os.getenv("PUSHER_CLUSTER"),
    ssl=True
)

# Trigger an event
pusher_client.trigger(
    f"private-orders.{order.id}",
    "order.updated",
    {
        "order_id": order.id,
        **broadcast_props({
            "order": order.dict()
        })
    }
)
```

## Best Practices

1. **Use throttling wisely**: High-frequency updates should have appropriate throttle values
2. **Broadcast values when possible**: Reduce server load by including prop values in events
3. **Keep channels focused**: Use specific channels (e.g., `orders.123`) rather than broad channels
4. **Combine with deferred**: Load slow data in the background, then keep it updated with live props
5. **Monitor your broadcaster**: Broadcasting can generate significant traffic at scale

## Reference

- [Inertia.js Live Props Documentation](https://inertiajs.com/live-props)
- [Laravel Broadcasting](https://laravel.com/docs/broadcasting)
- [Laravel Reverb](https://laravel.com/docs/reverb)
