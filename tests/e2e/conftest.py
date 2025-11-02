"""E2E test fixtures and configuration."""

import subprocess
import time
from typing import Generator

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def fastapi_server() -> Generator[str, None, None]:
    """Start the FastAPI server for E2E tests."""
    import sys
    from pathlib import Path
    import httpx

    # Add examples/fastapi to Python path so imports work
    fastapi_dir = Path(__file__).parent.parent.parent / "examples" / "fastapi"

    # Start the server with Python directly, not uv run
    # This ensures the server can import modules correctly in CI
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8888",
        ],
        cwd=str(fastapi_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready - poll until it responds
    base_url = "http://127.0.0.1:8888"
    for _ in range(30):  # Try for up to 3 seconds
        try:
            httpx.get(f"{base_url}/", timeout=0.5)
            break
        except (httpx.ConnectError, httpx.TimeoutException):
            time.sleep(0.1)
    else:
        # Server didn't start - print error output for debugging
        stdout, stderr = process.communicate(timeout=1)
        raise RuntimeError(
            f"Server failed to start!\nSTDOUT:\n{stdout.decode()}\n\nSTDERR:\n{stderr.decode()}"
        )

    # Yield the base URL
    yield base_url

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def page(page: Page, fastapi_server: str) -> Page:
    """Configure page with base URL."""
    page.set_default_timeout(10000)  # 10 second timeout
    return page
