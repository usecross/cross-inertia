"""Tests for partial reload functionality (not yet implemented)."""

import pytest
from fastapi.testclient import TestClient


class TestPartialReloads:
    """Test partial reload functionality per Inertia spec."""

    @pytest.mark.skip(reason="Partial reloads not yet implemented")
    def test_partial_data_header(self, client: TestClient):
        """Test that X-Inertia-Partial-Data header filters props."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Data": "message",
                "X-Inertia-Partial-Component": "TestComponent",
            },
        )

        data = response.json()
        # Should only include the requested prop
        assert "message" in data["props"]
        # Other props should not be included
        # (need a route with multiple props to test this properly)

    @pytest.mark.skip(reason="Partial reloads not yet implemented")
    def test_partial_component_mismatch(self, client: TestClient):
        """Test that partial reload is ignored if component doesn't match."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Data": "message",
                "X-Inertia-Partial-Component": "DifferentComponent",
            },
        )

        # Should return all props when component doesn't match
        data = response.json()
        assert "message" in data["props"]

    @pytest.mark.skip(reason="Partial reloads not yet implemented")
    def test_partial_except_header(self, client: TestClient):
        """Test that X-Inertia-Partial-Except excludes specific props."""
        # This would need a route with multiple props to test properly
        pass

    @pytest.mark.skip(reason="Partial reloads not yet implemented")
    def test_partial_reload_only_same_component(self, client: TestClient):
        """Test that partial reloads only work for same component."""
        # Partial reloads should only work when visiting the same component
        # If the destination component is different, all props should be returned
        pass
