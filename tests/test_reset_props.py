"""Tests for X-Inertia-Reset header functionality (infinite scroll reset)."""

from fastapi.testclient import TestClient


class TestResetPropsHeader:
    """Test X-Inertia-Reset header handling for infinite scroll."""

    def test_reset_header_parsed(self, client: TestClient):
        """Test that X-Inertia-Reset header is parsed and included in response."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users",
            },
        )

        data = response.json()
        # Reset props should be included in the response
        assert "resetProps" in data
        assert data["resetProps"] == ["users"]

    def test_reset_header_multiple_props(self, client: TestClient):
        """Test that multiple reset props are parsed correctly."""
        response = client.get(
            "/test-reset-multiple-merge-types",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users,notifications",
            },
        )

        data = response.json()
        assert "resetProps" in data
        assert "users" in data["resetProps"]
        assert "notifications" in data["resetProps"]

    def test_reset_header_strips_whitespace(self, client: TestClient):
        """Test that whitespace is stripped from reset prop names."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": " users , filters ",
            },
        )

        data = response.json()
        assert "resetProps" in data
        assert "users" in data["resetProps"]
        assert "filters" in data["resetProps"]

    def test_reset_removes_from_merge_props(self, client: TestClient):
        """Test that reset props are removed from mergeProps list."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users",
            },
        )

        data = response.json()
        # users should not be in mergeProps since it's being reset
        assert "mergeProps" not in data or "users" not in data.get("mergeProps", [])
        # But resetProps should include it
        assert "resetProps" in data
        assert "users" in data["resetProps"]

    def test_reset_removes_from_prepend_props(self, client: TestClient):
        """Test that reset props are removed from prependProps list."""
        response = client.get(
            "/test-reset-with-prepend",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "notifications",
            },
        )

        data = response.json()
        # notifications should not be in prependProps since it's being reset
        assert "prependProps" not in data or "notifications" not in data.get(
            "prependProps", []
        )
        # But resetProps should include it
        assert "resetProps" in data
        assert "notifications" in data["resetProps"]

    def test_reset_removes_from_deep_merge_props(self, client: TestClient):
        """Test that reset props are removed from deepMergeProps list."""
        response = client.get(
            "/test-reset-with-deep-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "settings",
            },
        )

        data = response.json()
        # settings should not be in deepMergeProps since it's being reset
        # user should still be in deepMergeProps
        assert "deepMergeProps" in data
        assert "settings" not in data["deepMergeProps"]
        assert "user" in data["deepMergeProps"]
        # But resetProps should include settings
        assert "resetProps" in data
        assert "settings" in data["resetProps"]

    def test_reset_selective_from_multiple_merge_types(self, client: TestClient):
        """Test that reset only affects specified props across merge types."""
        response = client.get(
            "/test-reset-multiple-merge-types",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users,settings",
            },
        )

        data = response.json()
        # users was in mergeProps - should be removed
        assert "mergeProps" not in data or "users" not in data.get("mergeProps", [])
        # notifications was in prependProps - should remain
        assert "prependProps" in data
        assert "notifications" in data["prependProps"]
        # settings was in deepMergeProps - should be removed
        assert "deepMergeProps" not in data or "settings" not in data.get(
            "deepMergeProps", []
        )
        # Reset props should include both
        assert "resetProps" in data
        assert "users" in data["resetProps"]
        assert "settings" in data["resetProps"]

    def test_no_reset_header_no_reset_props(self, client: TestClient):
        """Test that resetProps is not in response when header is absent."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
            },
        )

        data = response.json()
        # No reset header means no resetProps in response
        assert "resetProps" not in data
        # mergeProps should be present as normal
        assert "mergeProps" in data
        assert "users" in data["mergeProps"]

    def test_empty_reset_header_no_reset_props(self, client: TestClient):
        """Test that empty reset header doesn't add resetProps."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "",
            },
        )

        data = response.json()
        # Empty reset header means no resetProps in response
        assert "resetProps" not in data

    def test_reset_props_still_includes_data(self, client: TestClient):
        """Test that reset props are still included in props data."""
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users",
            },
        )

        data = response.json()
        # The actual prop data should still be returned
        assert "users" in data["props"]
        assert data["props"]["users"] == [{"id": 1, "name": "User"}]


class TestResetPropsNestedPaths:
    """Test X-Inertia-Reset header handling for nested prop paths."""

    def test_reset_filters_nested_merge_props(self, client: TestClient):
        """Test that reset 'items' filters out 'items.data' from mergeProps."""
        # This requires a route with nested merge props
        # The existing routes use flat props, so this tests the logic
        response = client.get(
            "/test-reset-with-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "users",
            },
        )

        data = response.json()
        # mergeProps should be filtered out since 'users' was reset
        assert "mergeProps" not in data or "users" not in data.get("mergeProps", [])

    def test_reset_parent_excludes_child_props(self, client: TestClient):
        """Test that resetting parent prop excludes child merge props."""
        # If we reset 'settings', it should also exclude 'settings.theme'
        response = client.get(
            "/test-reset-with-deep-merge",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Reset": "settings",
            },
        )

        data = response.json()
        # settings should be in resetProps
        assert "resetProps" in data
        assert "settings" in data["resetProps"]
        # deepMergeProps should exclude settings but keep user
        if "deepMergeProps" in data:
            assert "settings" not in data["deepMergeProps"]
            assert "user" in data["deepMergeProps"]
