"""Tests for Vite dev server process management."""

import asyncio
import sys

import pytest

from cross_inertia._config import configure_inertia, reset_config
from cross_inertia._vite import AsyncViteProcess, SyncViteProcess


@pytest.fixture(autouse=True)
def reset_config_after_test():
    yield
    reset_config()


class TestHealthUrl:
    def test_defaults_to_root_base(self):
        process = SyncViteProcess(port=5188)
        assert process.base == "/"
        assert process.health_url == "http://localhost:5188/@vite/client"

    def test_explicit_base_is_normalized(self):
        process = SyncViteProcess(port=5188, base="static/build")
        assert process.base == "/static/build/"
        assert process.health_url == "http://localhost:5188/static/build/@vite/client"

    def test_base_falls_back_to_shared_config(self):
        configure_inertia(vite_port=5189, vite_base="/static/build/")
        process = SyncViteProcess()
        assert process.health_url == "http://localhost:5189/static/build/@vite/client"

    def test_async_process_accepts_base(self):
        process = AsyncViteProcess(port=5190, base="/assets/")
        assert process.health_url == "http://localhost:5190/assets/@vite/client"


class TestStartupErrors:
    def test_exit_error_includes_command_and_recent_output(self):
        """A command that exits immediately should fail fast with useful context."""
        script = (
            'import sys; print("Usage: bun run [flags] <file or script>"); sys.exit(2)'
        )
        process = SyncViteProcess(
            command=[sys.executable, "-c", script],
            port=5191,
            startup_timeout=5.0,
            base="/static/build/",
        )

        with pytest.raises(RuntimeError) as excinfo:
            process.start()

        message = str(excinfo.value)
        assert "Vite exited with code 2" in message
        assert "--port" in message
        assert "5191" in message
        assert "http://localhost:5191/static/build/@vite/client" in message
        assert "Usage: bun run" in message

    def test_timeout_error_includes_health_url(self):
        """When Vite never becomes healthy the error says which URL was probed."""
        script = "import time; print('ready'); time.sleep(30)"
        process = SyncViteProcess(
            command=[sys.executable, "-c", script],
            port=5192,
            startup_timeout=0.5,
        )

        with pytest.raises(RuntimeError) as excinfo:
            process.start()

        message = str(excinfo.value)
        assert "did not start within 0.5s" in message
        assert "http://localhost:5192/@vite/client" in message
        assert process._process is None or process._process.poll() is not None


class TestAsyncStartupErrors:
    def test_exit_error_includes_recent_output(self):
        script = (
            'import sys; print("Usage: bun run [flags] <file or script>"); sys.exit(2)'
        )

        async def run_test():
            process = AsyncViteProcess(
                command=[sys.executable, "-c", script],
                port=5193,
                startup_timeout=5.0,
            )
            with pytest.raises(RuntimeError) as excinfo:
                await process.start()
            return str(excinfo.value)

        message = asyncio.run(run_test())
        assert "Vite exited with code 2" in message
        assert "http://localhost:5193/@vite/client" in message
        assert "Usage: bun run" in message
