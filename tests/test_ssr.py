"""Tests for Server-Side Rendering (SSR) support."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from cross_inertia._core import Inertia, InertiaResponse
from cross_inertia._ssr import InertiaSSR, SSRResponse
from cross_web import StarletteRequestAdapter


class TestSSRResponse:
    """Test the SSRResponse dataclass."""

    def test_ssr_response_creation(self):
        """Test SSRResponse can be created with head and body."""
        response = SSRResponse(
            head=["<title>Test</title>", "<meta name='description' content='test'>"],
            body="<div>Hello World</div>",
        )
        assert response.head == [
            "<title>Test</title>",
            "<meta name='description' content='test'>",
        ]
        assert response.body == "<div>Hello World</div>"

    def test_ssr_response_empty_values(self):
        """Test SSRResponse with empty values."""
        response = SSRResponse(head=[], body="")
        assert response.head == []
        assert response.body == ""


class _MockAsyncClient:
    """Simple async context manager used to mock httpx.AsyncClient."""

    def __init__(
        self, response: MagicMock | None = None, error: Exception | None = None
    ):
        self.response = response
        self.error = error
        self.get_calls: list[str] = []
        self.post_calls: list[tuple[str, dict]] = []
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.exited = True
        return False

    async def get(self, url: str):
        self.get_calls.append(url)
        if self.error:
            raise self.error
        assert self.response is not None
        return self.response

    async def post(self, url: str, json: dict):
        self.post_calls.append((url, json))
        if self.error:
            raise self.error
        assert self.response is not None
        return self.response


class TestInertiaSSR:
    """Test the InertiaSSR client."""

    def test_init_default_values(self):
        """Test InertiaSSR initializes with correct defaults."""
        ssr = InertiaSSR()
        assert ssr.url == "http://127.0.0.1:13714"
        assert ssr.timeout == 5.0
        assert ssr.enabled is True
        assert ssr._healthy is None

    def test_init_custom_values(self):
        """Test InertiaSSR initializes with custom values."""
        ssr = InertiaSSR(
            url="http://localhost:3000/",
            timeout=10.0,
            enabled=False,
        )
        assert ssr.url == "http://localhost:3000"  # Trailing slash stripped
        assert ssr.timeout == 10.0
        assert ssr.enabled is False

    def test_url_trailing_slash_stripped(self):
        """Test that trailing slashes are stripped from URL."""
        ssr = InertiaSSR(url="http://localhost:3000///")
        assert ssr.url == "http://localhost:3000"

    def test_render_returns_none_when_disabled(self):
        """Test that render returns None when SSR is disabled."""

        async def run_test():
            ssr = InertiaSSR(enabled=False)
            page_data = {
                "component": "TestComponent",
                "props": {"message": "Hello"},
                "url": "/test",
                "version": "1.0",
            }

            result = await ssr.render(page_data)
            assert result is None

        asyncio.run(run_test())

    def test_render_success(self):
        """Test successful SSR render."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "head": ["<title>Test</title>"],
                "body": "<div>Rendered</div>",
            }
            mock_response.raise_for_status = MagicMock()

            clients: list[_MockAsyncClient] = []

            def make_client(*args, **kwargs):
                client = _MockAsyncClient(response=mock_response)
                clients.append(client)
                return client

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                page_data = {
                    "component": "TestComponent",
                    "props": {"message": "Hello"},
                    "url": "/test",
                    "version": "1.0",
                }

                result = await ssr.render(page_data)

                assert result is not None
                assert isinstance(result, SSRResponse)
                assert result.head == ["<title>Test</title>"]
                assert result.body == "<div>Rendered</div>"
                assert len(clients) == 1
                assert clients[0].entered is True
                assert clients[0].exited is True
                assert clients[0].post_calls == [
                    ("http://127.0.0.1:13714/render", page_data)
                ]

        asyncio.run(run_test())

    def test_render_uses_fresh_client_for_each_event_loop(self):
        """Repeated render calls should not reuse a client across closed loops."""
        ssr = InertiaSSR()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "head": ["<title>SSR</title>"],
            "body": "<div>Rendered</div>",
        }
        mock_response.raise_for_status = MagicMock()

        clients: list[_MockAsyncClient] = []

        def make_client(*args, **kwargs):
            client = _MockAsyncClient(response=mock_response)
            clients.append(client)
            return client

        page_data = {
            "component": "TestComponent",
            "props": {"message": "Hello"},
            "url": "/test",
            "version": "1.0",
        }

        with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
            first = asyncio.run(ssr.render(page_data))
            second = asyncio.run(ssr.render(page_data))

        assert first is not None
        assert second is not None
        assert len(clients) == 2
        assert clients[0] is not clients[1]
        assert all(client.entered and client.exited for client in clients)

    def test_render_timeout(self):
        """Test that render returns None on timeout."""

        async def run_test():
            ssr = InertiaSSR()

            def make_client(*args, **kwargs):
                return _MockAsyncClient(error=httpx.TimeoutException("Timeout"))

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                page_data = {
                    "component": "TestComponent",
                    "props": {},
                    "url": "/test",
                    "version": "1.0",
                }

                result = await ssr.render(page_data)
                assert result is None

        asyncio.run(run_test())

    def test_render_http_error(self):
        """Test that render returns None on HTTP error."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            )

            def make_client(*args, **kwargs):
                return _MockAsyncClient(response=mock_response)

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                page_data = {
                    "component": "TestComponent",
                    "props": {},
                    "url": "/test",
                    "version": "1.0",
                }

                result = await ssr.render(page_data)
                assert result is None

        asyncio.run(run_test())

    def test_render_generic_exception(self):
        """Test that render returns None on generic exception."""

        async def run_test():
            ssr = InertiaSSR()

            def make_client(*args, **kwargs):
                return _MockAsyncClient(error=Exception("Connection failed"))

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                page_data = {
                    "component": "TestComponent",
                    "props": {},
                    "url": "/test",
                    "version": "1.0",
                }

                result = await ssr.render(page_data)
                assert result is None

        asyncio.run(run_test())

    def test_render_with_empty_response(self):
        """Test render handles response with missing fields gracefully."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}  # Empty response
            mock_response.raise_for_status = MagicMock()

            def make_client(*args, **kwargs):
                return _MockAsyncClient(response=mock_response)

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                page_data = {
                    "component": "TestComponent",
                    "props": {},
                    "url": "/test",
                    "version": "1.0",
                }

                result = await ssr.render(page_data)

                assert result is not None
                assert result.head == []
                assert result.body == ""

        asyncio.run(run_test())

    def test_health_check_success(self):
        """Test successful health check."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 200

            clients: list[_MockAsyncClient] = []

            def make_client(*args, **kwargs):
                client = _MockAsyncClient(response=mock_response)
                clients.append(client)
                return client

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                result = await ssr.health_check()

                assert result is True
                assert ssr._healthy is True
                assert len(clients) == 1
                assert clients[0].get_calls == ["http://127.0.0.1:13714/health"]
                assert clients[0].entered is True
                assert clients[0].exited is True

        asyncio.run(run_test())

    def test_health_check_unhealthy(self):
        """Test health check returns false for non-200 status."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 503

            def make_client(*args, **kwargs):
                return _MockAsyncClient(response=mock_response)

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                result = await ssr.health_check()

                assert result is False
                assert ssr._healthy is False

        asyncio.run(run_test())

    def test_health_check_uses_fresh_client_for_each_event_loop(self):
        """Repeated health checks should not reuse a client across closed loops."""
        ssr = InertiaSSR()

        mock_response = MagicMock()
        mock_response.status_code = 200

        clients: list[_MockAsyncClient] = []

        def make_client(*args, **kwargs):
            client = _MockAsyncClient(response=mock_response)
            clients.append(client)
            return client

        with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
            assert asyncio.run(ssr.health_check()) is True
            assert asyncio.run(ssr.health_check()) is True

        assert len(clients) == 2
        assert clients[0] is not clients[1]
        assert all(client.entered and client.exited for client in clients)

    def test_health_check_exception(self):
        """Test health check returns false on exception."""

        async def run_test():
            ssr = InertiaSSR()

            def make_client(*args, **kwargs):
                return _MockAsyncClient(error=Exception("Connection refused"))

            with patch("cross_inertia._ssr.httpx.AsyncClient", side_effect=make_client):
                result = await ssr.health_check()

                assert result is False
                assert ssr._healthy is False

        asyncio.run(run_test())


class TestInertiaResponseSSR:
    """Integration-style tests for SSR behavior in InertiaResponse."""

    def test_repeated_async_requests_render_with_ssr(self):
        """Repeated async FastAPI requests should not hit a closed-loop SSR client."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text(
                """<!DOCTYPE html>
<html>
<head>
    {{ inertia_head() | safe }}
</head>
<body>
    {{ inertia_body() | safe }}
</body>
</html>"""
            )

            inertia_response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url="http://localhost:5173",
                manifest_path="static/build/.vite/manifest.json",
                ssr_enabled=True,
            )
            inertia_response._is_dev = True

            app = FastAPI()

            def get_test_inertia(request: Request) -> Inertia:
                adapter = StarletteRequestAdapter(request)
                return Inertia(request, adapter, inertia_response)

            @app.get("/test")
            async def test_route(request: Request):
                inertia = get_test_inertia(request)
                return inertia.render("TestComponent", {"message": "Hello"})

            render_calls: list[dict] = []

            async def mock_render(page: dict):
                render_calls.append(page)
                return SSRResponse(
                    head=["<title>SSR Title</title>"],
                    body="<div id='app'>SSR Body</div>",
                )

            mock_client = AsyncMock()
            mock_client.render = mock_render
            inertia_response._vite_dev_ssr_client = mock_client

            client = TestClient(app)

            first = client.get("/test")
            second = client.get("/test")

            assert first.status_code == 200
            assert second.status_code == 200
            assert first.text.count("SSR Body") == 1
            assert second.text.count("SSR Body") == 1
            assert "SSR Title" in first.text
            assert "SSR Title" in second.text
            assert len(render_calls) == 2

    def test_ssr_failure_still_falls_back_to_csr(self):
        """SSR failure should still return the standard CSR response."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "templates"
            template_path.mkdir()
            (template_path / "app.html").write_text(
                """<!DOCTYPE html>
<html>
<head>
    {{ inertia_head() | safe }}
</head>
<body>
    {{ inertia_body() | safe }}
</body>
</html>"""
            )

            inertia_response = InertiaResponse(
                template_dir=str(template_path),
                vite_dev_url="http://localhost:5173",
                manifest_path="static/build/.vite/manifest.json",
                ssr_enabled=True,
            )
            inertia_response._is_dev = True

            app = FastAPI()

            def get_test_inertia(request: Request) -> Inertia:
                adapter = StarletteRequestAdapter(request)
                return Inertia(request, adapter, inertia_response)

            @app.get("/test")
            async def test_route(request: Request):
                inertia = get_test_inertia(request)
                return inertia.render("TestComponent", {"message": "Hello"})

            async def failing_render(page: dict):
                raise RuntimeError("SSR broken")

            mock_client = AsyncMock()
            mock_client.render = failing_render
            inertia_response._vite_dev_ssr_client = mock_client

            client = TestClient(app)
            response = client.get("/test")

            assert response.status_code == 200
            assert 'data-page="app"' in response.text
            assert 'id="app"' in response.text
