"""Test views for Django Inertia tests."""

from datetime import datetime, timezone

from django.views import View

from cross_inertia import defer, once, optional
from cross_inertia.django import render, location, inertia, InertiaViewMixin

FIXED_ONCE_EXPIRY = datetime(2030, 1, 1, tzinfo=timezone.utc)


def share_data(request):
    """Shared data for Django parity tests."""
    return {
        "auth": {"user": "alice"},
        "flash": {"msg": "saved"},
    }


def test_route(request):
    """Basic test route."""
    return render(request, "TestComponent", {"message": "Hello, World!"})


def multi_props_route(request):
    """Route with multiple props."""
    return render(
        request,
        "TestComponent",
        {
            "message": "Hello",
            "user": {"name": "John", "email": "john@example.com"},
            "count": 42,
            "items": ["a", "b", "c"],
        },
    )


def test_errors(request):
    """Route with validation errors."""
    return render(
        request,
        "TestComponent",
        {"message": "Hello"},
        errors={"field": "This field is required"},
    )


def test_submit(request):
    """POST route test."""
    return render(request, "Success", {"submitted": True})


def test_external_redirect(request):
    """External redirect test."""
    return location("https://github.com/login")


def nested_props_route(request):
    """Route with nested props and nested special wrappers."""
    return render(
        request,
        "TestComponent",
        {
            "profile": {
                "name": "John",
                "email": "john@example.com",
                "permissions": optional(lambda: ["invite"]),
            },
            "stats": {
                "count": 42,
                "items": ["a", "b"],
            },
        },
    )


def deferred_props_route(request):
    """Route with deferred props for parity checks."""
    return render(
        request,
        "TestComponent",
        {
            "user": "John",
            "analytics": defer(lambda: {"views": 1000}, group="default"),
        },
    )


def once_props_route(request):
    """Route with once props and once+defer composition."""
    return render(
        request,
        "TestComponent",
        {
            "plans": once(
                lambda: ["starter", "pro"],
                key="plans-cache",
                until=FIXED_ONCE_EXPIRY,
            ),
            "permissions": once(
                defer(lambda: ["invite"], group="sidebar"),
                key="permissions-cache",
            ),
        },
    )


def reset_route(request):
    """Route with reset-compatible merge metadata."""
    return render(
        request,
        "TestComponent",
        {
            "users": [{"id": 1, "name": "User"}],
            "filters": {"role": "admin"},
        },
        merge_props=["users"],
    )


def history_route(request):
    """Route with history flags enabled."""
    return render(
        request,
        "TestComponent",
        {"message": "History"},
        encrypt_history=True,
        clear_history=True,
    )


@inertia("DecoratorTest")
def test_decorator(request):
    """Test the @inertia decorator."""
    return {"decorated": True, "message": "From decorator"}


class TestClassView(InertiaViewMixin, View):
    """Test class-based view with mixin."""

    component = "ClassViewTest"

    def get_props(self, request, *args, **kwargs):
        return {"class_based": True, "method": "GET"}

    def get(self, request):
        return self.render_inertia(request)

    def post(self, request):
        return self.render_inertia(request, extra_props={"method": "POST"})
