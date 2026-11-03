"""Prop type wrappers for Inertia.js."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any


class optional:
    """
    Mark a prop as optional - only evaluated when explicitly requested.

    Works like functools.partial - you can pass args and kwargs that will be
    applied when the prop is evaluated.

    Optional props are excluded from initial page loads. They are only included
    and evaluated when requested via partial reloads with `only: ['prop_name']`.

    This is useful for expensive queries that users may not always need.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            user = get_current_user()
            return inertia.render("Dashboard", {
                "user": user,
                # These are only loaded when explicitly requested
                "permissions": optional(get_permissions, user.id),
                "activity": optional(get_activity, user_id=user.id, limit=100),
                "billing": optional(get_billing_history, user.id),
            })

        # Frontend - load optional prop on demand:
        router.reload({ only: ['permissions'] })

        # Load multiple:
        router.reload({ only: ['permissions', 'activity'] })
    """

    # TODO: Add proper typing with ParamSpec and TypeVar for better IDE support
    def __init__(self, callback: Callable[..., Any], *args: Any, **kwargs: Any):
        """
        Create an optional prop.

        Args:
            callback: A callable that returns the prop value when invoked.
            *args: Positional arguments to pass to the callback.
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("optional() requires a callable")
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)


class always:
    """
    Mark a prop as always included - even during partial reloads.

    Props wrapped with always() are always included in every Inertia response,
    even during partial reloads when only specific props are requested.

    Works like functools.partial - you can pass args and kwargs, or just a value.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            return inertia.render("Dashboard", {
                "user": get_user(),
                "flash": always(get_flash_messages),  # Always included
                "notifications": always(get_notifications, user_id=user.id),
            })

        # Frontend partial reload - flash is STILL included:
        router.reload({ only: ['user'] })  # flash is also returned
    """

    def __init__(self, value_or_callback: Any, *args: Any, **kwargs: Any):
        """
        Create an always prop.

        Args:
            value_or_callback: A value or callable that returns the prop value.
            *args: Positional arguments to pass to the callback (if callable).
            **kwargs: Keyword arguments to pass to the callback (if callable).
        """
        self.value_or_callback = value_or_callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Get the value, invoking the callback if needed."""
        if callable(self.value_or_callback):
            return self.value_or_callback(*self.args, **self.kwargs)
        return self.value_or_callback


class defer:
    """
    Mark a prop as deferred - loaded after the initial page render.

    Deferred props are excluded from the initial page load and loaded in a
    subsequent request after the page renders. This improves perceived performance
    by allowing the page to display immediately while slower data loads in the
    background.

    Unlike optional() props which require explicit requests from the frontend,
    deferred props are automatically loaded by the Inertia client after mount.

    Props can be grouped together to be loaded in the same request by providing
    a group name. Props in different groups are loaded in parallel.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            user = get_current_user()
            return inertia.render("Dashboard", {
                "user": user,  # Loaded immediately
                # These are loaded after page renders:
                "analytics": defer(get_analytics),  # Default group
                "notifications": defer(get_notifications, user.id),  # Default group
                # Load permissions separately (parallel with default group):
                "permissions": defer(get_permissions, user.id, group="permissions"),
            })

        # Frontend - use the Deferred component:
        <Deferred data="analytics" fallback={<Loading />}>
            <AnalyticsChart analytics={analytics} />
        </Deferred>

    Reference:
        https://inertiajs.com/deferred-props
    """

    def __init__(
        self,
        callback: Callable[..., Any],
        *args: Any,
        group: str = "default",
        rescue: bool = False,
        **kwargs: Any,
    ):
        """
        Create a deferred prop.

        Args:
            callback: A callable that returns the prop value when invoked.
            *args: Positional arguments to pass to the callback.
            group: Name of the group for batching requests. Props in the same
                   group are loaded together; different groups load in parallel.
                   Defaults to "default".
            rescue: Omit failures and report the prop in ``rescuedProps`` instead
                    of failing the entire partial response.
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("defer() requires a callable")
        self.callback = callback
        self.args = args
        self.group = group
        self.rescue = rescue
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)


class once:
    """
    Mark a prop as remembered by the client across navigations.

    Once props are resolved on the first Inertia visit, then skipped on
    subsequent non-partial Inertia responses when the client indicates it
    already has a remembered value.

    The wrapped value can be a plain value, a callable, or another prop
    wrapper such as defer(), optional(), or always().
    """

    def __init__(
        self,
        value_or_callback: Any,
        *,
        key: str | None = None,
        fresh: bool = False,
        until: datetime | timedelta | int | None = None,
    ):
        self.value_or_callback = value_or_callback
        self.key = key
        self.fresh = fresh
        self.until = until

    def __call__(self) -> Any:
        """Get the value, invoking the callback if needed."""
        if callable(self.value_or_callback):
            return self.value_or_callback()
        return self.value_or_callback

    def expires_at(self) -> int | None:
        """Return the expiration timestamp in milliseconds, if configured."""
        if self.until is None:
            return None

        if isinstance(self.until, datetime):
            return int(self.until.timestamp() * 1000)

        if isinstance(self.until, timedelta):
            return int((datetime.now().timestamp() + self.until.total_seconds()) * 1000)

        return int((datetime.now().timestamp() + self.until) * 1000)


class live:
    """
    Mark a prop as live - automatically refreshes when a broadcast event fires.

    Live props listen for broadcast events and refresh themselves using partial
    reloads. This is ideal for real-time updates like order statuses, unread
    message counts, or dashboard metrics without polling.

    When a broadcast event fires, Inertia makes a partial reload to fetch the
    latest value of the prop. Props listening for the same event on the same
    channel are refreshed together in a single request.

    Live props can be combined with other prop wrappers like defer(), once(),
    optional(), and always() for flexible behavior.

    Example:
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

        # Combine with defer for background loading + live updates:
        "metrics": defer(get_metrics).live(
            on="metrics.updated",
            channel={"name": "dashboard", "type": "private"}
        )

        # Frontend setup with Laravel Echo:
        createInertiaApp({
            live: echo()
        })

    Reference:
        https://inertiajs.com/live-props
    """

    def __init__(
        self,
        callback: Callable[..., Any],
        *args: Any,
        on: str | list[str] | None = None,
        channel: dict[str, str] | list[dict[str, str]] | None = None,
        throttle: int | None = None,
        **kwargs: Any,
    ):
        """
        Create a live prop.

        Args:
            callback: A callable that returns the prop value when invoked.
            *args: Positional arguments to pass to the callback.
            on: Event name(s) that trigger refresh. Can be a single event name
                or a list of event names.
            channel: Broadcasting channel(s) to listen on. Each channel should be
                     a dict with 'name' and 'type' keys. Type can be 'public',
                     'private', 'presence', or 'encrypted-private'. If not provided,
                     events should include channel information.
            throttle: Optional throttle in milliseconds. Limits refresh rate to
                      at most once per throttle period. Defaults to 1000ms (1 second).
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("live() requires a callable")
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.on = [on] if isinstance(on, str) else (on or [])
        self.channel = [channel] if isinstance(channel, dict) else (channel or [])
        self.throttle = throttle

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)


def broadcast_props(props: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare props to be broadcast with an event, avoiding server requests.

    When a broadcast event includes prop values using this helper, Inertia
    clients can update the page without making a server request. This is
    especially useful for high-traffic scenarios (e.g., a dashboard open
    in many tabs).

    Use this in your event's broadcast payload:

    Example:
        class OrderUpdated:
            def __init__(self, order):
                self.order = order

            def broadcast_with(self):
                return {
                    "order_id": self.order.id,
                    **broadcast_props({
                        "order": OrderResource(self.order).dict(),
                    })
                }

    The broadcast event payload should include these under the __inertia.props
    key for the Inertia client to recognize them.

    Args:
        props: Dictionary mapping prop paths to values. Supports dot notation
               for nested props (e.g., "user.profile.name").

    Returns:
        Dictionary with "__inertia" key containing the props structure.

    Reference:
        https://inertiajs.com/live-props#broadcasting-props
    """
    return {
        "__inertia": {
            "props": props,
        }
    }
