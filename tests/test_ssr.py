"""Tests for Server-Side Rendering (SSR) support."""

import asyncio

import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from inertia._ssr import InertiaSSR, SSRResponse


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


class TestInertiaSSR:
    """Test the InertiaSSR client."""

    def test_init_default_values(self):
        """Test InertiaSSR initializes with correct defaults."""
        ssr = InertiaSSR()
        assert ssr.url == "http://127.0.0.1:13714"
        assert ssr.timeout == 5.0
        assert ssr.enabled is True
        assert ssr._client is None
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

    def test_get_client_creates_client(self):
        """Test that _get_client creates a new client if none exists."""

        async def run_test():
            ssr = InertiaSSR()
            assert ssr._client is None

            client = await ssr._get_client()
            assert client is not None
            assert isinstance(client, httpx.AsyncClient)
            assert ssr._client is client

            # Calling again returns the same client
            client2 = await ssr._get_client()
            assert client2 is client

            await ssr.close()

        asyncio.run(run_test())

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

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.object(ssr, "_get_client", return_value=mock_client):
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

                mock_client.post.assert_called_once_with(
                    "http://127.0.0.1:13714/render",
                    json=page_data,
                )

        asyncio.run(run_test())

    def test_render_timeout(self):
        """Test that render returns None on timeout."""

        async def run_test():
            ssr = InertiaSSR()

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

            with patch.object(ssr, "_get_client", return_value=mock_client):
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
            error = httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            )

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=error)

            with patch.object(ssr, "_get_client", return_value=mock_client):
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

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=Exception("Connection failed"))

            with patch.object(ssr, "_get_client", return_value=mock_client):
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

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.object(ssr, "_get_client", return_value=mock_client):
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

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            with patch.object(ssr, "_get_client", return_value=mock_client):
                result = await ssr.health_check()

                assert result is True
                assert ssr._healthy is True
                mock_client.get.assert_called_once_with("http://127.0.0.1:13714/health")

        asyncio.run(run_test())

    def test_health_check_unhealthy(self):
        """Test health check returns false for non-200 status."""

        async def run_test():
            ssr = InertiaSSR()

            mock_response = MagicMock()
            mock_response.status_code = 503

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            with patch.object(ssr, "_get_client", return_value=mock_client):
                result = await ssr.health_check()

                assert result is False
                assert ssr._healthy is False

        asyncio.run(run_test())

    def test_health_check_exception(self):
        """Test health check returns false on exception."""

        async def run_test():
            ssr = InertiaSSR()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))

            with patch.object(ssr, "_get_client", return_value=mock_client):
                result = await ssr.health_check()

                assert result is False
                assert ssr._healthy is False

        asyncio.run(run_test())

    def test_close_client(self):
        """Test closing the HTTP client."""

        async def run_test():
            ssr = InertiaSSR()

            # Create a mock client
            mock_client = AsyncMock()
            mock_client.aclose = AsyncMock()
            ssr._client = mock_client

            await ssr.close()

            mock_client.aclose.assert_called_once()
            assert ssr._client is None

        asyncio.run(run_test())

    def test_close_no_client(self):
        """Test closing when no client exists."""

        async def run_test():
            ssr = InertiaSSR()
            assert ssr._client is None

            # Should not raise
            await ssr.close()
            assert ssr._client is None

        asyncio.run(run_test())
