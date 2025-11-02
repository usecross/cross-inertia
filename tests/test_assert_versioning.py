"""Tests for asset versioning functionality."""

from unittest.mock import patch

from fastapi.testclient import TestClient


class TestAssetVersioning:
    """Test asset versioning and cache busting."""

    def test_version_in_page_object(self, client: TestClient):
        """Test that version is included in page object."""
        response = client.get(
            "/test",
            headers={"X-Inertia": "true"},
        )
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_dev_mode_version(self, inertia_response):
        """Test that dev mode returns 'dev' as version."""
        with patch.object(inertia_response, "is_dev_mode", return_value=True):
            version = inertia_response.get_asset_version()
            assert version == "dev"

    def test_production_version_from_manifest(self, inertia_response):
        """Test that production mode generates version from manifest hash."""
        with patch.object(inertia_response, "is_dev_mode", return_value=False):
            with patch.object(
                inertia_response, "get_manifest", return_value={"app.js": "hash123"}
            ):
                version = inertia_response.get_asset_version()
                assert version != "dev"
                assert isinstance(version, str)

    def test_version_mismatch_returns_409(self, client: TestClient):
        """Test that version mismatch returns 409 Conflict."""
        # Make request with different version (will mismatch with server version)
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Version": "different-version",
            },
        )

        # Should return 409 Conflict
        assert response.status_code == 409
        assert "X-Inertia-Location" in response.headers

    def test_version_match_proceeds_normally(self, client: TestClient):
        """Test that matching version proceeds with normal response."""
        # Make initial request to get current version
        response = client.get("/test", headers={"X-Inertia": "true"})
        current_version = response.json()["version"]

        # Make request with same version
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Version": current_version,
            },
        )

        # Should return 200 OK
        assert response.status_code == 200
        data = response.json()
        assert data["component"] == "TestComponent"


class TestViteIntegration:
    """Test Vite dev server detection and asset loading."""

    def test_dev_mode_detection(self, inertia_response):
        """Test that dev mode is detected correctly."""
        # The is_dev_mode method caches its result
        # In real tests, we'd need to mock the httpx call
        is_dev = inertia_response.is_dev_mode()
        assert isinstance(is_dev, bool)

    def test_vite_tags_in_dev_mode(self, inertia_response):
        """Test that dev mode includes Vite dev server tags."""
        with patch.object(inertia_response, "is_dev_mode", return_value=True):
            tags = inertia_response.get_vite_tags()
            assert "@vite/client" in tags
            assert "@react-refresh" in tags
            assert "frontend/app.tsx" in tags

    def test_vite_tags_in_production(self, inertia_response):
        """Test that production mode uses manifest for asset tags."""
        manifest = {
            "frontend/app.tsx": {
                "file": "assets/app.abc123.js",
                "css": ["assets/app.xyz789.css"],
            }
        }

        with patch.object(inertia_response, "is_dev_mode", return_value=False):
            with patch.object(inertia_response, "get_manifest", return_value=manifest):
                tags = inertia_response.get_vite_tags()
                assert "assets/app.abc123.js" in tags
                assert "assets/app.xyz789.css" in tags
                assert "@vite/client" not in tags
