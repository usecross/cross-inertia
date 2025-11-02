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

    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)
