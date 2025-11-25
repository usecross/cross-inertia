"""Tests for Inertia prefetch support."""

from fastapi.testclient import TestClient


class TestPrefetchSupport:
    """Test prefetch request detection and handling."""

    def test_detects_prefetch_request(self, client: TestClient):
        """Test that Purpose: prefetch header is properly detected."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "Purpose": "prefetch",
            },
        )
        # Prefetch requests should return normal Inertia response
        assert response.status_code == 200
        assert response.headers.get("X-Inertia") == "true"
        assert response.headers.get("Content-Type") == "application/json"

        # Response should have correct structure
        data = response.json()
        assert "component" in data
        assert "props" in data
        assert "url" in data
        assert "version" in data

    def test_prefetch_returns_same_response_as_normal_request(self, client: TestClient):
        """Test that prefetch requests return the same data as normal Inertia requests."""
        # Normal Inertia request
        normal_response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
            },
        )

        # Prefetch request
        prefetch_response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "Purpose": "prefetch",
            },
        )

        # Both should return the same data
        normal_data = normal_response.json()
        prefetch_data = prefetch_response.json()

        assert normal_data["component"] == prefetch_data["component"]
        assert normal_data["props"] == prefetch_data["props"]
        assert normal_data["url"] == prefetch_data["url"]
        # Version might vary in some cases, but structure should be same
        assert "version" in prefetch_data

    def test_prefetch_with_partial_reload(self, client: TestClient):
        """Test that prefetch works with partial reloads."""
        response = client.get(
            "/multi-props",
            headers={
                "X-Inertia": "true",
                "Purpose": "prefetch",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "message,user",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Only requested props should be included
        assert "message" in data["props"]
        assert "user" in data["props"]
        # Other props should not be included
        assert "count" not in data["props"]
        assert "items" not in data["props"]

    def test_purpose_header_without_inertia_header(self, client: TestClient):
        """Test that Purpose header alone doesn't make it a prefetch request."""
        # Purpose header without X-Inertia should return HTML (initial page load)
        response = client.get(
            "/test",
            headers={
                "Purpose": "prefetch",
            },
        )

        assert response.status_code == 200
        # Should return HTML, not JSON
        assert "text/html" in response.headers.get("Content-Type")
        assert "data-page=" in response.text

    def test_prefetch_with_errors(self, client: TestClient):
        """Test that prefetch requests handle errors correctly."""
        response = client.get(
            "/with-errors",
            headers={
                "X-Inertia": "true",
                "Purpose": "prefetch",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" in data["props"]
        assert data["props"]["errors"]["field"] == "This field is required"

    def test_prefetch_with_different_purpose_value(self, client: TestClient):
        """Test that only Purpose: prefetch is detected as prefetch."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "Purpose": "other",
            },
        )

        # Should still work as normal Inertia request
        assert response.status_code == 200
        assert response.headers.get("X-Inertia") == "true"
