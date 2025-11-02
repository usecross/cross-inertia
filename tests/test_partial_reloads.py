"""Tests for partial reload functionality (not yet implemented)."""

from fastapi.testclient import TestClient


class TestPartialReloads:
    """Test partial reload functionality per Inertia spec."""

    def test_partial_data_header(self, client: TestClient):
        """Test that X-Inertia-Partial-Data header filters props."""
        response = client.get(
            "/multi-props",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Data": "message,count",
                "X-Inertia-Partial-Component": "TestComponent",
            },
        )

        data = response.json()
        # Should only include the requested props
        assert "message" in data["props"]
        assert "count" in data["props"]
        # Other props should not be included
        assert "user" not in data["props"]
        assert "items" not in data["props"]

    def test_partial_component_mismatch(self, client: TestClient):
        """Test that partial reload is ignored if component doesn't match."""
        response = client.get(
            "/multi-props",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Data": "message",
                "X-Inertia-Partial-Component": "DifferentComponent",
            },
        )

        # Should return all props when component doesn't match
        data = response.json()
        assert "message" in data["props"]
        assert "user" in data["props"]
        assert "count" in data["props"]
        assert "items" in data["props"]

    def test_partial_except_header(self, client: TestClient):
        """Test that X-Inertia-Partial-Except excludes specific props."""
        response = client.get(
            "/multi-props",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Except": "user,items",
                "X-Inertia-Partial-Component": "TestComponent",
            },
        )

        data = response.json()
        # Should include everything except the excluded props
        assert "message" in data["props"]
        assert "count" in data["props"]
        assert "user" not in data["props"]
        assert "items" not in data["props"]

    def test_partial_reload_only_same_component(self, client: TestClient):
        """Test that partial reloads only work for same component."""
        # When requesting partial data but component doesn't match, return all props
        response = client.get(
            "/multi-props",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Data": "message",
                "X-Inertia-Partial-Component": "WrongComponent",
            },
        )

        data = response.json()
        # Should return ALL props because component doesn't match
        assert len(data["props"]) == 4  # message, user, count, items
        assert "message" in data["props"]
        assert "user" in data["props"]
        assert "count" in data["props"]
        assert "items" in data["props"]
