"""Test views for Django Inertia tests."""

from django.views import View

from inertia.django import render, location, inertia, InertiaViewMixin


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
