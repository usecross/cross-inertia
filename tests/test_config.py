"""Tests for the unified configuration module."""

import socket

import pytest

from inertia._config import (
    InertiaConfig,
    configure_inertia,
    find_available_port,
    get_config,
    reset_config,
)


@pytest.fixture(autouse=True)
def reset_config_after_test():
    """Reset config after each test to avoid state leakage."""
    yield
    reset_config()


class TestFindAvailablePort:
    """Tests for find_available_port function."""

    def test_finds_port_in_range(self):
        """Should find an available port in the given range."""
        port = find_available_port(start=10000, end=10100)
        assert 10000 <= port < 10100

    def test_port_is_actually_available(self):
        """The returned port should be bindable."""
        port = find_available_port(start=10000, end=10100)
        # Should be able to bind to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))

    def test_raises_when_no_port_available(self):
        """Should raise RuntimeError when no port is available."""
        # Use a very small range and occupy all ports
        occupied_sockets = []
        try:
            for port in range(10200, 10203):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("127.0.0.1", port))
                occupied_sockets.append(s)

            with pytest.raises(RuntimeError, match="No available port found"):
                find_available_port(start=10200, end=10203)
        finally:
            for s in occupied_sockets:
                s.close()


class TestInertiaConfig:
    """Tests for InertiaConfig dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        config = InertiaConfig()
        assert config.vite_port == 5173
        assert config.vite_host == "localhost"
        assert config.vite_entry == "frontend/app.tsx"
        assert config.vite_command == "bun run dev"
        assert config.template_dir == "templates"
        assert config.ssr_enabled is False

    def test_vite_dev_url_with_explicit_port(self):
        """vite_dev_url should use the configured port."""
        config = InertiaConfig(vite_port=5188, vite_host="localhost")
        assert config.vite_dev_url == "http://localhost:5188"

    def test_vite_dev_url_with_auto_port(self):
        """vite_dev_url should use auto-selected port."""
        config = InertiaConfig(vite_port="auto")
        url = config.vite_dev_url
        assert url.startswith("http://localhost:")
        # Port should be in the default range
        port = int(url.split(":")[-1])
        assert 5173 <= port < 5273

    def test_resolved_vite_port_cached(self):
        """resolved_vite_port should be cached after first access."""
        config = InertiaConfig(vite_port="auto")
        port1 = config.resolved_vite_port
        port2 = config.resolved_vite_port
        assert port1 == port2

    def test_ssr_health_url(self):
        """ssr_health_url should combine ssr_url and health_path."""
        config = InertiaConfig(
            ssr_url="http://127.0.0.1:13714",
            ssr_health_path="/health",
        )
        assert config.ssr_health_url == "http://127.0.0.1:13714/health"

    def test_get_vite_command_with_port_string(self):
        """Should append --port to string command."""
        config = InertiaConfig(vite_port=5188, vite_command="bun run dev")
        cmd = config.get_vite_command_with_port()
        assert cmd == "bun run dev --port 5188"

    def test_get_vite_command_with_port_list(self):
        """Should append --port to list command."""
        config = InertiaConfig(vite_port=5188, vite_command=["bun", "run", "dev"])
        cmd = config.get_vite_command_with_port()
        assert cmd == ["bun", "run", "dev", "--port", "5188"]

    def test_get_vite_command_with_auto_port(self):
        """Should use resolved port for auto selection."""
        config = InertiaConfig(vite_port="auto", vite_command="bun run dev")
        cmd = config.get_vite_command_with_port()
        assert "--port" in cmd
        # Port should be a number
        port_str = cmd.split("--port ")[1]
        assert port_str.isdigit()


class TestConfigureInertia:
    """Tests for configure_inertia function."""

    def test_returns_config(self):
        """Should return the created config."""
        config = configure_inertia(vite_port=5188)
        assert isinstance(config, InertiaConfig)
        assert config.vite_port == 5188

    def test_sets_global_config(self):
        """Should set the global config accessible via get_config()."""
        configure_inertia(vite_port=5199, ssr_enabled=True)
        config = get_config()
        assert config.vite_port == 5199
        assert config.ssr_enabled is True

    def test_all_parameters(self):
        """Should accept all configuration parameters."""
        config = configure_inertia(
            vite_port=5200,
            vite_host="0.0.0.0",
            vite_entry="src/main.tsx",
            vite_command="npm run dev",
            vite_timeout=60.0,
            template_dir="views",
            manifest_path="dist/manifest.json",
            ssr_enabled=True,
            ssr_url="http://localhost:3000",
            ssr_command="node ssr.js",
            ssr_timeout=20.0,
            ssr_health_path="/ping",
        )
        assert config.vite_port == 5200
        assert config.vite_host == "0.0.0.0"
        assert config.vite_entry == "src/main.tsx"
        assert config.vite_command == "npm run dev"
        assert config.vite_timeout == 60.0
        assert config.template_dir == "views"
        assert config.manifest_path == "dist/manifest.json"
        assert config.ssr_enabled is True
        assert config.ssr_url == "http://localhost:3000"
        assert config.ssr_command == "node ssr.js"
        assert config.ssr_timeout == 20.0
        assert config.ssr_health_path == "/ping"


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_default_if_not_configured(self):
        """Should return default config if configure_inertia wasn't called."""
        config = get_config()
        assert isinstance(config, InertiaConfig)
        assert config.vite_port == 5173

    def test_returns_configured_config(self):
        """Should return the configured config."""
        configure_inertia(vite_port=5300)
        config = get_config()
        assert config.vite_port == 5300


class TestResetConfig:
    """Tests for reset_config function."""

    def test_resets_to_default(self):
        """Should reset config so get_config returns defaults."""
        configure_inertia(vite_port=5400)
        reset_config()
        config = get_config()
        assert config.vite_port == 5173
