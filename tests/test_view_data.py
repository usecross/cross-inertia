"""Tests for view data feature."""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


@pytest.fixture
def temp_template_dir_with_view_data():
    """Create a temporary templates directory with template that uses view_data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "templates"
        template_path.mkdir()

        # Create app.html template that uses view_data variables
        (template_path / "app.html").write_text(
            """<!DOCTYPE html>
<html>
<head>
    <title>{% if page_title %}{{ page_title }}{% else %}Test{% endif %}</title>
    {% if og_meta %}
    <meta property="og:title" content="{{ og_meta.title }}">
    <meta property="og:description" content="{{ og_meta.description }}">
    {% endif %}
    {{ vite_tags | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>"""
        )
        yield str(template_path)


@pytest.fixture
def app_with_view_data(temp_template_dir_with_view_data):
    """Create a FastAPI test application with view_data routes."""
    from inertia._core import Inertia, InertiaResponse
    from lia import StarletteRequestAdapter

    app = FastAPI()

    inertia_response = InertiaResponse(
        template_dir=temp_template_dir_with_view_data,
        vite_dev_url="http://localhost:5173",
        manifest_path="static/build/.vite/manifest.json",
    )

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-view-data")
    def test_view_data_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"message": "Hello"},
            view_data={
                "page_title": "Test Page",
                "og_meta": {
                    "title": "Test OG Title",
                    "description": "Test OG Description",
                },
            },
        )

    @app.get("/test-view-data-complex")
    def test_view_data_complex_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"message": "Hello"},
            view_data={
                "page_title": "Complex Page",
                "og_meta": {
                    "title": "Complex OG",
                    "description": "Complex Description",
                },
            },
        )

    @app.get("/test-chaining")
    def test_chaining_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.encrypt_history().render(
            "TestComponent",
            {"message": "Hello"},
            view_data={"page_title": "Chained Title"},
        )

    return app


@pytest.fixture
def view_data_client(app_with_view_data):
    """Create a test client for view_data tests."""
    return TestClient(app_with_view_data)


class TestViewData:
    """Test the view data feature for passing extra data to templates."""

    def test_view_data_in_html_template(self, view_data_client: TestClient):
        """Test that view_data adds data to template context."""
        response = view_data_client.get("/test-view-data")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type")

        html = response.text
        # Check that view_data variables are in the HTML
        assert "<title>Test Page</title>" in html
        assert '<meta property="og:title" content="Test OG Title">' in html
        assert '<meta property="og:description" content="Test OG Description">' in html

    def test_view_data_not_in_page_props(self, view_data_client: TestClient):
        """Test that view_data is NOT included in page props."""
        response = view_data_client.get("/test-view-data")
        assert response.status_code == 200

        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        # Check that view_data is NOT in page props
        assert "page_title" not in page_data["props"]
        assert "og_meta" not in page_data["props"]

        # Check that component props are still there
        assert page_data["props"]["message"] == "Hello"

    def test_view_data_not_in_xhr_response(self, view_data_client: TestClient):
        """Test that view_data is NOT included in Inertia XHR requests."""
        response = view_data_client.get(
            "/test-view-data",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        # View data should NOT be in page props for XHR requests
        assert "page_title" not in data["props"]
        assert "og_meta" not in data["props"]
        assert data["props"]["message"] == "Hello"

    def test_view_data_with_complex_structure(self, view_data_client: TestClient):
        """Test view_data with complex nested structures."""
        response = view_data_client.get("/test-view-data-complex")
        assert response.status_code == 200

        html = response.text
        # Check that view_data variables are in the HTML
        assert "<title>Complex Page</title>" in html
        assert '<meta property="og:title" content="Complex OG">' in html

        # Verify view_data is not in page props
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        assert "page_title" not in page_data["props"]
        assert "og_meta" not in page_data["props"]
        assert page_data["props"]["message"] == "Hello"

    def test_view_data_with_method_chaining(self, view_data_client: TestClient):
        """Test that view_data works with method chaining."""
        response = view_data_client.get("/test-chaining")
        assert response.status_code == 200

        html = response.text
        # Check that chaining worked - title should be set
        assert "<title>Chained Title</title>" in html

        # Verify both encryption and view_data worked
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        assert page_data["encryptHistory"] is True
        assert "page_title" not in page_data["props"]
