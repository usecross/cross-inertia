"""Tests for the dev-mode Vite tags emitted by InertiaResponse."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cross_inertia._config import configure_inertia, reset_config
from cross_inertia._core import InertiaResponse


@pytest.fixture(autouse=True)
def reset_config_after_test():
    yield
    reset_config()


@pytest.fixture
def template_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "templates"
        path.mkdir()
        (path / "app.html").write_text("<html></html>")
        yield str(path)


def test_dev_tags_default_to_root_base(template_dir):
    response = InertiaResponse(
        template_dir=template_dir,
        vite_dev_url="http://localhost:5173",
        vite_entry="frontend/app.tsx",
    )
    response._is_dev = True
    tags = response.get_vite_tags()

    assert 'src="http://localhost:5173/@vite/client"' in tags
    assert 'src="http://localhost:5173/frontend/app.tsx"' in tags
    assert 'from "http://localhost:5173/@react-refresh"' in tags


def test_dev_tags_honour_configured_vite_base(template_dir):
    configure_inertia(vite_port=5174, vite_host="127.0.0.1", vite_base="/static/build/")
    response = InertiaResponse(template_dir=template_dir, vite_entry="src/app.tsx")
    response._is_dev = True
    tags = response.get_vite_tags()

    assert 'src="http://127.0.0.1:5174/static/build/@vite/client"' in tags
    assert 'src="http://127.0.0.1:5174/static/build/src/app.tsx"' in tags
    assert 'from "http://127.0.0.1:5174/static/build/@react-refresh"' in tags


def test_explicit_vite_base_is_normalized(template_dir):
    response = InertiaResponse(
        template_dir=template_dir,
        vite_dev_url="http://localhost:5173",
        vite_base="static/build",
    )
    assert response.vite_base == "/static/build/"
    assert (
        response.vite_dev_asset_url("@vite/client")
        == "http://localhost:5173/static/build/@vite/client"
    )


def test_dev_mode_probe_uses_vite_base(template_dir):
    response = InertiaResponse(
        template_dir=template_dir,
        vite_dev_url="http://localhost:5173",
        vite_base="/static/build/",
    )
    probe = MagicMock(status_code=200)

    with patch("cross_inertia._core.httpx.get", return_value=probe) as get:
        assert response.is_dev_mode() is True

    assert get.call_args.args[0] == "http://localhost:5173/static/build/@vite/client"
