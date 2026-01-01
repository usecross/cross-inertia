"""Prop type wrappers for Inertia.js."""

from __future__ import annotations

from typing import Any, Callable


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
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("defer() requires a callable")
        self.callback = callback
        self.args = args
        self.group = group
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)
