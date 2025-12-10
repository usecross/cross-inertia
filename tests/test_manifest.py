"""Tests for Vite manifest handling."""

import tempfile
from pathlib import Path

import pytest

from inertia import ManifestNotFoundError
from inertia._core import InertiaResponse


class TestManifestNotFound:
    """Test manifest not found error handling."""

    def test_raises_error_when_manifest_missing(self):
        """Should raise ManifestNotFoundError when manifest file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text("<html></html>")

            response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url=None,  # Force production mode
                manifest_path=str(Path(tmpdir) / "nonexistent" / "manifest.json"),
            )

            # Force production mode detection
            response._is_dev = False

            with pytest.raises(ManifestNotFoundError) as exc_info:
                response.get_manifest()

            assert "manifest.json" in str(exc_info.value)
            assert "vite build" in str(exc_info.value)

    def test_error_message_includes_path(self):
        """Error message should include the manifest path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text("<html></html>")

            custom_path = "/custom/path/to/manifest.json"
            response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url=None,
                manifest_path=custom_path,
            )
            response._is_dev = False

            with pytest.raises(ManifestNotFoundError) as exc_info:
                response.get_manifest()

            assert custom_path in str(exc_info.value)

    def test_loads_manifest_when_exists(self):
        """Should load manifest successfully when file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text("<html></html>")

            # Create manifest file
            manifest_path = Path(tmpdir) / "manifest.json"
            manifest_path.write_text('{"frontend/app.tsx": {"file": "app.js"}}')

            response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url=None,
                manifest_path=str(manifest_path),
            )
            response._is_dev = False

            manifest = response.get_manifest()
            assert "frontend/app.tsx" in manifest
            assert manifest["frontend/app.tsx"]["file"] == "app.js"

    def test_get_vite_tags_raises_in_production_without_manifest(self):
        """get_vite_tags should raise when manifest missing in production."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text("<html></html>")

            response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url=None,
                manifest_path=str(Path(tmpdir) / "missing" / "manifest.json"),
                vite_entry="frontend/app.tsx",
            )
            response._is_dev = False

            with pytest.raises(ManifestNotFoundError):
                response.get_vite_tags()


class TestManifestNotFoundErrorExport:
    """Test that ManifestNotFoundError is properly exported."""

    def test_import_from_inertia(self):
        """Should be importable from main inertia module."""
        from inertia import ManifestNotFoundError

        assert ManifestNotFoundError is not None
        assert issubclass(ManifestNotFoundError, Exception)

    def test_import_from_core(self):
        """Should be importable from _core module."""
        from inertia._core import ManifestNotFoundError

        assert ManifestNotFoundError is not None
