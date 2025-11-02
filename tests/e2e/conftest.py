"""E2E test fixtures and configuration."""

import subprocess
import time
from typing import Generator

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def fastapi_server() -> Generator[str, None, None]:
    """Start the FastAPI server for E2E tests."""
    # Start the server
    process = subprocess.Popen(
        ["uv", "run", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8888"],
        cwd="examples/fastapi",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Wait for server to be ready
    time.sleep(3)
    
    # Yield the base URL
    yield "http://127.0.0.1:8888"
    
    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def page(page: Page, fastapi_server: str) -> Page:
    """Configure page with base URL."""
    page.set_default_timeout(10000)  # 10 second timeout
    return page
