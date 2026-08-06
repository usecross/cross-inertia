"""Tests for Django Inertia render function."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock
from unittest.mock import patch

from django.test import override_settings


@pytest.fixture
def setup_inertia(django_inertia_response):
    """Set up and tear down Inertia response for tests."""
    from cross_inertia.django.shortcuts import reset_inertia_response
    import cross_inertia.django.shortcuts as shortcuts

    shortcuts._inertia_response = django_inertia_response
    yield
    reset_inertia_response()


def test_initial_page_load_returns_html(client, setup_inertia):
    """Initial page load should return HTML with page data."""
    response = client.get("/test/")
    assert response.status_code == 200
    assert "text/html" in response["Content-Type"]
    assert response["Vary"] == "X-Inertia"

    content = response.content.decode()
    assert 'script data-page="app"' in content
    assert "TestComponent" in content


def test_inertia_request_returns_json(client, setup_inertia):
    """Inertia XHR request should return JSON."""
    response = client.get(
        "/test/",
        HTTP_X_INERTIA="true",
    )
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response["X-Inertia"] == "true"
    assert response["Vary"] == "X-Inertia"

    data = response.json()
    assert data["component"] == "TestComponent"
    assert data["props"]["message"] == "Hello, World!"
    assert "url" in data
    assert "version" in data


def test_version_conflict_varies_on_inertia_header(rf, setup_inertia):
    from cross_inertia.django import render

    request = rf.get(
        "/version/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_VERSION="stale",
    )
    response = render(request, "Versioned")

    assert response.status_code == 409
    assert response["Vary"] == "X-Inertia"


def test_render_with_multiple_props(client, setup_inertia):
    """Should render with multiple props correctly."""
    response = client.get(
        "/multi-props/",
        HTTP_X_INERTIA="true",
    )
    data = response.json()

    assert data["props"]["message"] == "Hello"
    assert data["props"]["user"]["name"] == "John"
    assert data["props"]["count"] == 42
    assert data["props"]["items"] == ["a", "b", "c"]


def test_render_with_errors(client, setup_inertia):
    """Should include validation errors in props."""
    response = client.get(
        "/with-errors/",
        HTTP_X_INERTIA="true",
    )
    data = response.json()

    assert "errors" in data["props"]
    assert data["props"]["errors"]["field"] == "This field is required"


def test_render_shortcut_accepts_flash_and_preserve_fragment(rf, setup_inertia):
    from cross_inertia.django import render

    request = rf.get("/flash/", HTTP_X_INERTIA="true")
    response = render(
        request,
        "Flash",
        flash={"message": "Saved"},
        preserve_fragment=True,
    )
    data = json.loads(response.content)

    assert data["flash"] == {"message": "Saved"}
    assert data["preserveFragment"] is True


def test_render_shortcut_accepts_custom_status(rf, setup_inertia):
    from cross_inertia.django import render

    request = rf.get("/forbidden/", HTTP_X_INERTIA="true")
    response = render(
        request,
        "ErrorPage",
        {"status": 403},
        status_code=403,
    )

    assert response.status_code == 403
    assert json.loads(response.content)["props"]["status"] == 403


def test_render_shortcut_preserves_existing_positional_arguments(rf, setup_inertia):
    from cross_inertia.django import render

    request = rf.get("/legacy/", HTTP_X_INERTIA="true")
    response = render(
        request,
        "Legacy",
        {"items": [1]},
        None,
        False,
        False,
        ["items"],
    )

    assert json.loads(response.content)["mergeProps"] == ["items"]


def test_render_shortcut_accepts_schema_argument(rf, setup_inertia):
    """Django render shortcut should validate and serialize props with schema."""
    from pydantic import BaseModel

    from cross_inertia.django import render

    class UserRecord(BaseModel):
        id: int
        name: str
        password_hash: str

    class UserPublic(BaseModel):
        id: int
        name: str

    class PostPublic(BaseModel):
        id: int
        title: str

    class CountsByStatus(BaseModel):
        draft: int
        published: int

    class PostsIndexProps(BaseModel):
        user: UserPublic
        posts: list[PostPublic]
        counts: CountsByStatus

    def posts_view(request):
        return render(
            request,
            "Posts/Index",
            {
                "user": UserRecord(id=1, name="Ada", password_hash="secret"),
                "posts": [{"id": 10, "title": "Draft"}],
                "counts": lambda: CountsByStatus(draft=1, published=0),
            },
            schema=PostsIndexProps,
        )

    request = rf.get("/posts/", HTTP_X_INERTIA="true")
    response = posts_view(request)
    data = json.loads(response.content)

    assert response.status_code == 200
    assert response["X-Inertia"] == "true"
    assert data["props"] == {
        "user": {"id": 1, "name": "Ada"},
        "posts": [{"id": 10, "title": "Draft"}],
        "counts": {"draft": 1, "published": 0},
    }


def test_external_redirect_returns_409(client, setup_inertia):
    """External redirect should return 409 with location header."""
    response = client.get("/external-redirect/")
    assert response.status_code == 409
    assert response["X-Inertia-Location"] == "https://github.com/login"


def test_inertia_decorator(client, setup_inertia):
    """@inertia decorator should wrap view props."""
    response = client.get(
        "/decorator/",
        HTTP_X_INERTIA="true",
    )
    data = response.json()

    assert data["component"] == "DecoratorTest"
    assert data["props"]["decorated"] is True
    assert data["props"]["message"] == "From decorator"


def test_inertia_decorator_supports_async_views(rf, setup_inertia):
    from cross_inertia.django import inertia

    @inertia("AsyncDecoratorTest")
    async def async_view(request):
        return {"decorated": True}

    request = rf.get("/async-decorator/", HTTP_X_INERTIA="true")
    response = asyncio.run(async_view(request))
    data = json.loads(response.content)

    assert data["component"] == "AsyncDecoratorTest"
    assert data["props"]["decorated"] is True


def test_inertia_decorator_supports_asgiref_marked_views(rf, setup_inertia):
    from asgiref.sync import markcoroutinefunction

    from cross_inertia.django import inertia

    def marked_view(request):
        async def result():
            return {"decorated": True}

        return result()

    markcoroutinefunction(marked_view)
    wrapped_view = inertia("MarkedDecoratorTest")(marked_view)

    request = rf.get("/marked-decorator/", HTTP_X_INERTIA="true")
    response = asyncio.run(wrapped_view(request))
    data = json.loads(response.content)

    assert data["component"] == "MarkedDecoratorTest"
    assert data["props"]["decorated"] is True


def test_inertia_decorator_passes_through_async_streaming_responses(rf, setup_inertia):
    from django.http import StreamingHttpResponse

    from cross_inertia.django import inertia

    @inertia("Ignored")
    async def async_view(request):
        return StreamingHttpResponse(iter([b"streamed"]))

    request = rf.get("/stream/")
    response = asyncio.run(async_view(request))

    assert isinstance(response, StreamingHttpResponse)
    assert b"".join(response.streaming_content) == b"streamed"


def test_class_based_view_get(client, setup_inertia):
    """Class-based view GET should work."""
    response = client.get(
        "/class-view/",
        HTTP_X_INERTIA="true",
    )
    data = response.json()

    assert data["component"] == "ClassViewTest"
    assert data["props"]["class_based"] is True
    assert data["props"]["method"] == "GET"


def test_class_based_view_post(client, setup_inertia):
    """Class-based view POST should work with extra props."""
    response = client.post(
        "/class-view/",
        HTTP_X_INERTIA="true",
    )
    data = response.json()

    assert data["component"] == "ClassViewTest"
    assert data["props"]["class_based"] is True
    assert data["props"]["method"] == "POST"


def test_ssr_html_response_includes_ssr_head_and_body(client, django_inertia_response):
    from cross_inertia._ssr import SSRResponse
    from cross_inertia.django.shortcuts import reset_inertia_response
    import cross_inertia.django.shortcuts as shortcuts

    django_inertia_response.ssr_enabled = True
    mock_client = AsyncMock()
    mock_client.render = AsyncMock(
        return_value=SSRResponse(
            head=["<title>SSR Title</title>"],
            body="<main><h1>SSR Body</h1></main>",
        )
    )
    django_inertia_response._vite_dev_ssr_client = mock_client
    shortcuts._inertia_response = django_inertia_response

    try:
        response = client.get("/test/")
    finally:
        reset_inertia_response()

    content = response.content.decode()
    assert response.status_code == 200
    assert "<title>SSR Title</title>" in content
    assert "<main><h1>SSR Body</h1></main>" in content


def test_ssr_failure_falls_back_to_csr_html(client, django_inertia_response):
    from cross_inertia.django.shortcuts import reset_inertia_response
    import cross_inertia.django.shortcuts as shortcuts

    django_inertia_response.ssr_enabled = True
    mock_client = AsyncMock()
    mock_client.render = AsyncMock(side_effect=RuntimeError("SSR unavailable"))
    django_inertia_response._vite_dev_ssr_client = mock_client
    shortcuts._inertia_response = django_inertia_response

    try:
        response = client.get("/test/")
    finally:
        reset_inertia_response()

    content = response.content.decode()
    assert response.status_code == 200
    assert 'script data-page="app"' in content
    assert "TestComponent" in content


@override_settings(STATIC_URL="assets/")
def test_production_vite_tags_use_static_url_prefix(temp_template_dir):
    from cross_inertia.django.conf import inertia_settings
    from cross_inertia.django.response import DjangoInertiaResponse

    inertia_settings.reload()
    response = DjangoInertiaResponse(
        template_name="app.html",
        vite_dev_url=None,
        manifest_path="static/build/.vite/manifest.json",
        ssr_enabled=False,
    )
    response._is_dev = False

    manifest = {
        "frontend/app.tsx": {
            "file": "assets/app.js",
            "css": ["assets/app.css"],
        }
    }

    with patch.object(response, "get_manifest", return_value=manifest):
        tags = response.get_vite_tags()

    assert "/assets/build/assets/app.js" in tags
    assert "/assets/build/assets/app.css" in tags
    inertia_settings.reload()


def test_django_vite_tags_allow_explicit_react_refresh_configuration():
    from cross_inertia.django.response import DjangoInertiaResponse

    react_response = DjangoInertiaResponse(
        vite_entry="resources/js/app.ts",
        vite_react_refresh=True,
    )
    react_response._is_dev = True
    assert "@react-refresh" in react_response.get_vite_tags()

    vue_response = DjangoInertiaResponse(
        vite_entry="resources/js/app.tsx",
        vite_react_refresh=False,
    )
    vue_response._is_dev = True
    assert "@react-refresh" not in vue_response.get_vite_tags()
