"""Tests for SSR server lifespan management."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from inertia._config import reset_config
from inertia.fastapi.experimental import (
    SSRServer,
    SSRServerError,
    create_ssr_lifespan,
    inertia_lifespan,
)


@pytest.fixture(autouse=True)
def reset_config_after_test():
    """Reset config after each test to avoid state leakage."""
    yield
    reset_config()


class TestSSRServer:
    """Test the SSRServer class."""

    def test_init_default_values(self):
        """Test SSRServer initializes with correct defaults."""
        server = SSRServer()
        assert server.command == "bun dist/ssr/ssr.js"
        assert server.cwd is None
        assert server.health_url == "http://127.0.0.1:13714/health"
        assert server.startup_timeout == 10.0
        assert server.env is None
        assert server._process is None

    def test_init_custom_values(self):
        """Test SSRServer initializes with custom values."""
        server = SSRServer(
            command="node server.js",
            cwd="/app",
            health_url="http://localhost:3000/health",
            startup_timeout=30.0,
            env={"NODE_ENV": "production"},
        )
        assert server.command == "node server.js"
        assert server.cwd == "/app"
        assert server.health_url == "http://localhost:3000/health"
        assert server.startup_timeout == 30.0
        assert server.env == {"NODE_ENV": "production"}

    def test_init_with_list_command(self):
        """Test SSRServer accepts a list command."""
        server = SSRServer(command=["node", "server.js", "--port", "3000"])
        assert server.command == ["node", "server.js", "--port", "3000"]

    def test_is_running_false_when_no_process(self):
        """Test is_running returns False when no process exists."""
        server = SSRServer()
        assert server.is_running is False

    def test_is_running_false_when_process_exited(self):
        """Test is_running returns False when process has exited."""
        server = SSRServer()
        mock_process = MagicMock()
        mock_process.returncode = 1  # Process exited
        server._process = mock_process
        assert server.is_running is False

    def test_is_running_true_when_process_running(self):
        """Test is_running returns True when process is running."""
        server = SSRServer()
        mock_process = MagicMock()
        mock_process.returncode = None  # Process still running
        server._process = mock_process
        assert server.is_running is True

    def test_start_logs_warning_if_already_running(self):
        """Test start logs warning if server already running."""

        async def run_test():
            server = SSRServer()
            mock_process = MagicMock()
            mock_process.returncode = None
            server._process = mock_process

            with patch("inertia.fastapi.experimental.lifespan.logger") as mock_logger:
                await server.start()
                mock_logger.warning.assert_called_once_with(
                    "SSR server is already running"
                )

        asyncio.run(run_test())

    def test_start_raises_on_command_not_found(self):
        """Test start raises SSRServerError when command not found."""

        async def run_test():
            server = SSRServer(command="nonexistent_command_xyz")

            with pytest.raises(SSRServerError) as exc_info:
                await server.start()
            # The error can be "not found" or exit code 127 (command not found)
            error_msg = str(exc_info.value)
            assert "not found" in error_msg or "127" in error_msg

        asyncio.run(run_test())

    def test_start_with_successful_health_check(self):
        """Test successful server start with health check."""

        async def run_test():
            server = SSRServer(command="echo test", startup_timeout=2.0)

            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None

            mock_response = MagicMock()
            mock_response.status_code = 200

            with patch(
                "asyncio.create_subprocess_shell",
                new=AsyncMock(return_value=mock_process),
            ):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__ = AsyncMock(
                        return_value=mock_client
                    )
                    mock_client_class.return_value.__aexit__ = AsyncMock(
                        return_value=None
                    )

                    await server.start()
                    assert server._process is mock_process

                    # Cleanup
                    server._process = None

        asyncio.run(run_test())

    def test_start_raises_on_health_check_timeout(self):
        """Test start raises SSRServerError when health check times out."""

        async def run_test():
            import httpx

            server = SSRServer(
                command="sleep 10",
                startup_timeout=0.1,  # Very short timeout
            )

            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.wait = AsyncMock()

            with patch(
                "asyncio.create_subprocess_shell",
                new=AsyncMock(return_value=mock_process),
            ):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("fail"))
                    mock_client_class.return_value.__aenter__ = AsyncMock(
                        return_value=mock_client
                    )
                    mock_client_class.return_value.__aexit__ = AsyncMock(
                        return_value=None
                    )

                    with pytest.raises(SSRServerError) as exc_info:
                        await server.start()
                    assert "did not become healthy" in str(exc_info.value)

        asyncio.run(run_test())

    def test_stop_when_no_process(self):
        """Test stop does nothing when no process exists."""

        async def run_test():
            server = SSRServer()
            await server.stop()  # Should not raise
            assert server._process is None

        asyncio.run(run_test())

    def test_stop_terminates_process(self):
        """Test stop terminates the process gracefully."""

        async def run_test():
            server = SSRServer()
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.wait = AsyncMock()

            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            server._process = mock_process
            server._output_task = None

            await server.stop()

            if sys.platform == "win32":
                mock_process.terminate.assert_called_once()
            else:
                mock_process.send_signal.assert_called_once()

            assert server._process is None

        asyncio.run(run_test())

    def test_stop_force_kills_on_timeout(self):
        """Test stop force kills process if graceful shutdown times out."""

        async def run_test():
            server = SSRServer()
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.kill = MagicMock()

            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            # First wait times out, second succeeds
            mock_process.wait = AsyncMock(side_effect=[asyncio.TimeoutError(), None])

            server._process = mock_process
            server._output_task = None

            await server.stop()

            mock_process.kill.assert_called_once()
            assert server._process is None

        asyncio.run(run_test())


class TestCreateSSRLifespan:
    """Test the create_ssr_lifespan context manager."""

    def test_create_ssr_lifespan_starts_and_stops_server(self):
        """Test that create_ssr_lifespan starts and stops the server."""

        async def run_test():
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.wait = AsyncMock()
            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            mock_response = MagicMock()
            mock_response.status_code = 200

            with patch(
                "asyncio.create_subprocess_shell",
                new=AsyncMock(return_value=mock_process),
            ):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__ = AsyncMock(
                        return_value=mock_client
                    )
                    mock_client_class.return_value.__aexit__ = AsyncMock(
                        return_value=None
                    )

                    async with create_ssr_lifespan(
                        command="echo test",
                        startup_timeout=2.0,
                    ) as server:
                        assert server.is_running is True

                    # After exiting context, server should be stopped
                    assert server._process is None

        asyncio.run(run_test())

    def test_create_ssr_lifespan_yields_server(self):
        """Test that create_ssr_lifespan yields the SSRServer instance."""

        async def run_test():
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.wait = AsyncMock()
            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            mock_response = MagicMock()
            mock_response.status_code = 200

            with patch(
                "asyncio.create_subprocess_shell",
                new=AsyncMock(return_value=mock_process),
            ):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__ = AsyncMock(
                        return_value=mock_client
                    )
                    mock_client_class.return_value.__aexit__ = AsyncMock(
                        return_value=None
                    )

                    async with create_ssr_lifespan(
                        command="echo test",
                        startup_timeout=2.0,
                    ) as server:
                        assert isinstance(server, SSRServer)

        asyncio.run(run_test())

    def test_create_ssr_lifespan_custom_config(self):
        """Test create_ssr_lifespan with custom configuration."""

        async def run_test():
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.wait = AsyncMock()
            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            mock_response = MagicMock()
            mock_response.status_code = 200

            with patch(
                "asyncio.create_subprocess_shell",
                new=AsyncMock(return_value=mock_process),
            ):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__ = AsyncMock(
                        return_value=mock_client
                    )
                    mock_client_class.return_value.__aexit__ = AsyncMock(
                        return_value=None
                    )

                    async with create_ssr_lifespan(
                        command="node server.js",
                        cwd="/custom/path",
                        health_url="http://localhost:3000/health",
                        startup_timeout=15.0,
                        env={"NODE_ENV": "test"},
                    ) as server:
                        assert server.command == "node server.js"
                        assert server.cwd == "/custom/path"
                        assert server.health_url == "http://localhost:3000/health"
                        assert server.startup_timeout == 15.0
                        assert server.env == {"NODE_ENV": "test"}

        asyncio.run(run_test())


class TestInertiaLifespan:
    """Test the inertia_lifespan context manager."""

    def test_inertia_lifespan_uses_env_vars(self):
        """Test that inertia_lifespan reads configuration from environment."""

        async def run_test():
            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.wait = AsyncMock()
            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            mock_response = MagicMock()
            mock_response.status_code = 200

            env_vars = {
                "INERTIA_SSR_ENABLED": "1",  # Enable SSR via env var
                "INERTIA_SSR_COMMAND": "custom_command",
                "INERTIA_SSR_CWD": "/custom/cwd",
                "INERTIA_SSR_HEALTH_URL": "http://custom:1234/health",
                "INERTIA_SSR_TIMEOUT": "20",
            }

            with patch.dict(os.environ, env_vars, clear=False):
                with patch(
                    "asyncio.create_subprocess_shell",
                    new=AsyncMock(return_value=mock_process),
                ) as mock_subprocess:
                    with patch("httpx.AsyncClient") as mock_client_class:
                        mock_client = AsyncMock()
                        mock_client.get = AsyncMock(return_value=mock_response)
                        mock_client_class.return_value.__aenter__ = AsyncMock(
                            return_value=mock_client
                        )
                        mock_client_class.return_value.__aexit__ = AsyncMock(
                            return_value=None
                        )

                        mock_app = MagicMock()
                        async with inertia_lifespan(mock_app):
                            # Verify the subprocess was called with our custom command
                            mock_subprocess.assert_called_once()
                            call_args = mock_subprocess.call_args
                            assert call_args[0][0] == "custom_command"
                            assert call_args[1]["cwd"] == "/custom/cwd"

        asyncio.run(run_test())

    def test_inertia_lifespan_uses_defaults(self):
        """Test that inertia_lifespan uses defaults when env vars not set."""
        from inertia import configure_inertia

        async def run_test():
            # Enable SSR via config (since env var defaults won't enable it)
            configure_inertia(ssr_enabled=True)

            mock_process = MagicMock()
            mock_process.returncode = None
            mock_process.stdout = None
            mock_process.stderr = None
            mock_process.wait = AsyncMock()
            if sys.platform == "win32":
                mock_process.terminate = MagicMock()
            else:
                mock_process.send_signal = MagicMock()

            mock_response = MagicMock()
            mock_response.status_code = 200

            # Clear any existing env vars that would override config
            env_vars_to_remove = [
                "INERTIA_SSR_ENABLED",
                "INERTIA_SSR_COMMAND",
                "INERTIA_SSR_CWD",
                "INERTIA_SSR_HEALTH_URL",
                "INERTIA_SSR_TIMEOUT",
            ]
            clean_env = {
                k: v for k, v in os.environ.items() if k not in env_vars_to_remove
            }

            with patch.dict(os.environ, clean_env, clear=True):
                with patch(
                    "asyncio.create_subprocess_shell",
                    new=AsyncMock(return_value=mock_process),
                ) as mock_subprocess:
                    with patch("httpx.AsyncClient") as mock_client_class:
                        mock_client = AsyncMock()
                        mock_client.get = AsyncMock(return_value=mock_response)
                        mock_client_class.return_value.__aenter__ = AsyncMock(
                            return_value=mock_client
                        )
                        mock_client_class.return_value.__aexit__ = AsyncMock(
                            return_value=None
                        )

                        mock_app = MagicMock()
                        async with inertia_lifespan(mock_app):
                            # Verify defaults were used
                            mock_subprocess.assert_called_once()
                            call_args = mock_subprocess.call_args
                            assert call_args[0][0] == "bun dist/ssr/ssr.js"
                            assert call_args[1]["cwd"] is None

        asyncio.run(run_test())


class TestImports:
    """Test that lifespan utilities are properly exported."""

    def test_import_from_inertia_fastapi_experimental(self):
        """Test importing from the inertia.fastapi.experimental module."""
        from inertia.fastapi.experimental import (
            inertia_lifespan,
            create_ssr_lifespan,
            SSRServer,
            SSRServerError,
        )

        assert inertia_lifespan is not None
        assert create_ssr_lifespan is not None
        assert SSRServer is not None
        assert SSRServerError is not None

    def test_import_from_lifespan_module(self):
        """Test importing from the lifespan module directly."""
        from inertia.fastapi.experimental.lifespan import (
            inertia_lifespan,
            create_ssr_lifespan,
            SSRServer,
            SSRServerError,
        )

        assert inertia_lifespan is not None
        assert create_ssr_lifespan is not None
        assert SSRServer is not None
        assert SSRServerError is not None
