"""Pytest configuration and fixtures for Inertia tests."""

import tempfile
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


@pytest.fixture
def temp_template_dir():
    """Create a temporary templates directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "templates"
        template_path.mkdir()

        # Create a basic app.html template
        (template_path / "app.html").write_text(
            """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    {{ vite_tags | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>"""
        )
        yield str(template_path)


@pytest.fixture
def inertia_response(temp_template_dir):
    """Create an InertiaResponse instance for testing."""
    from inertia._core import InertiaResponse

    return InertiaResponse(
        template_dir=temp_template_dir,
        vite_dev_url="http://localhost:5173",
        manifest_path="static/build/.vite/manifest.json",
    )


@pytest.fixture
def app(inertia_response):
    """Create a FastAPI test application."""
    app = FastAPI()

    # Override the default inertia response with our test instance
    def get_test_inertia(request: Request):
        from inertia._core import Inertia
        from lia import StarletteRequestAdapter

        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test")
    def test_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {"message": "Hello, World!"})

    @app.get("/multi-props")
    def multi_props_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "message": "Hello",
                "user": {"name": "John", "email": "john@example.com"},
                "count": 42,
                "items": ["a", "b", "c"],
            },
        )

    @app.get("/with-errors")
    def test_errors(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"message": "Hello"},
            errors={"field": "This field is required"},
        )

    @app.post("/submit")
    def test_submit(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("Success", {"submitted": True})

    # External redirect test routes
    @app.get("/test-external-redirect")
    def test_external_redirect(request: Request):
        inertia = get_test_inertia(request)
        return inertia.location("https://github.com/login")

    @app.get("/test-relative-redirect")
    def test_relative_redirect(request: Request):
        inertia = get_test_inertia(request)
        return inertia.location("/legacy/admin")

    @app.get("/test-oauth-redirect")
    def test_oauth_redirect(request: Request):
        inertia = get_test_inertia(request)
        oauth_url = (
            "https://github.com/login/oauth/authorize"
            "?client_id=abc123"
            "&redirect_uri=https://example.com/callback"
        )
        return inertia.location(oauth_url)

    @app.get("/test-maps-redirect")
    def test_maps_redirect(request: Request):
        inertia = get_test_inertia(request)
        address = "123 Main St, San Francisco, CA"
        return inertia.location(f"https://maps.google.com/?q={address}")

    # History encryption test routes
    @app.get("/test-encrypt-history")
    def test_encrypt_history(request: Request):
        inertia = get_test_inertia(request)
        inertia.encrypt_history()
        return inertia.render("TestComponent", {"message": "Encrypted page"})

    @app.get("/test-clear-history")
    def test_clear_history(request: Request):
        inertia = get_test_inertia(request)
        inertia.clear_history()
        return inertia.render("TestComponent", {"message": "Clearing history"})

    @app.get("/test-encrypt-and-clear")
    def test_encrypt_and_clear(request: Request):
        inertia = get_test_inertia(request)
        inertia.encrypt_history()
        inertia.clear_history()
        return inertia.render("TestComponent", {"message": "Both enabled"})

    @app.get("/test-method-chaining")
    def test_method_chaining(request: Request):
        inertia = get_test_inertia(request)
        # Test that methods return self for chaining
        inertia.encrypt_history().clear_history()
        return inertia.render("TestComponent", {"message": "Chained"})

    @app.get("/test-encrypt-false")
    def test_encrypt_false(request: Request):
        inertia = get_test_inertia(request)
        inertia.encrypt_history(False)
        return inertia.render("TestComponent", {"message": "Not encrypted"})

    @app.get("/test-clear-false")
    def test_clear_false(request: Request):
        inertia = get_test_inertia(request)
        inertia.clear_history(False)
        return inertia.render("TestComponent", {"message": "Not clearing"})

    # Merge props test routes
    @app.get("/test-merge-props")
    def test_merge_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"items": ["item1", "item2"]},
            merge_props=["items"],
        )

    @app.get("/test-prepend-props")
    def test_prepend_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"notifications": ["new1", "new2"]},
            prepend_props=["notifications"],
        )

    @app.get("/test-deep-merge-props")
    def test_deep_merge_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"settings": {"theme": "dark"}},
            deep_merge_props=["settings"],
        )

    @app.get("/test-match-props-on")
    def test_match_props_on(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"items": [{"id": 1, "name": "Item"}]},
            match_props_on=["id"],
        )

    @app.get("/test-all-merge-props")
    def test_all_merge_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"items": [{"id": 1, "name": "Item"}]},
            merge_props=["items"],
            match_props_on=["id"],
        )

    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)
