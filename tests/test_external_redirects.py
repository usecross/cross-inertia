"""Tests for external redirects feature."""

from fastapi.testclient import TestClient


class TestExternalRedirects:
    """Test external redirect functionality."""

    def test_location_returns_409_with_header(self, client: TestClient):
        """Test that location() returns 409 Conflict with X-Inertia-Location header."""
        response = client.get("/test-external-redirect")

        assert response.status_code == 409
        assert response.headers.get("X-Inertia-Location") == "https://github.com/login"

    def test_location_with_absolute_url(self, client: TestClient):
        """Test external redirect to absolute URL."""
        response = client.get("/test-external-redirect")

        assert response.status_code == 409
        location = response.headers.get("X-Inertia-Location")
        assert location.startswith("https://")

    def test_location_with_relative_url(self, client: TestClient):
        """Test external redirect to relative URL."""
        response = client.get("/test-relative-redirect")

        assert response.status_code == 409
        assert response.headers.get("X-Inertia-Location") == "/legacy/admin"

    def test_location_from_inertia_request(self, client: TestClient):
        """Test external redirect from an Inertia XHR request."""
        response = client.get(
            "/test-external-redirect",
            headers={
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        assert response.status_code == 409
        assert response.headers.get("X-Inertia-Location") == "https://github.com/login"

    def test_location_from_normal_request(self, client: TestClient):
        """Test external redirect from a normal (non-Inertia) request."""
        response = client.get("/test-external-redirect")

        # Should work the same for both Inertia and non-Inertia requests
        assert response.status_code == 409
        assert response.headers.get("X-Inertia-Location") == "https://github.com/login"

    def test_location_with_query_params(self, client: TestClient):
        """Test external redirect preserves query parameters."""
        response = client.get("/test-oauth-redirect")

        assert response.status_code == 409
        location = response.headers.get("X-Inertia-Location")
        assert "client_id=" in location
        assert "redirect_uri=" in location

    def test_location_google_maps_example(self, client: TestClient):
        """Test external redirect to Google Maps (real-world example)."""
        response = client.get("/test-maps-redirect")

        assert response.status_code == 409
        location = response.headers.get("X-Inertia-Location")
        assert location.startswith("https://maps.google.com")
        assert "?q=" in location
