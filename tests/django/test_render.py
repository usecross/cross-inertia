"""Tests for Django Inertia render function."""

import pytest


@pytest.fixture
def setup_inertia(django_inertia_response):
    """Set up and tear down Inertia response for tests."""
    from inertia.django.shortcuts import reset_inertia_response
    import inertia.django.shortcuts as shortcuts

    shortcuts._inertia_response = django_inertia_response
    yield
    reset_inertia_response()


def test_initial_page_load_returns_html(client, setup_inertia):
    """Initial page load should return HTML with page data."""
    response = client.get("/test/")
    assert response.status_code == 200
    assert "text/html" in response["Content-Type"]

    content = response.content.decode()
    assert "data-page=" in content
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
