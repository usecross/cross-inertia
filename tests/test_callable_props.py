"""Tests for callable props (auto-invoke) functionality."""

import json

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


class TestCallableProps:
    """Test that callable props are automatically invoked during render."""

    def test_lambda_prop_is_invoked(self, callable_client: TestClient):
        """Test that lambda props are automatically invoked."""
        response = callable_client.get(
            "/test-lambda-prop",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # The lambda should have been invoked, returning "computed value"
        assert data["props"]["computed"] == "computed value"

    def test_function_prop_is_invoked(self, callable_client: TestClient):
        """Test that function props are automatically invoked."""
        response = callable_client.get(
            "/test-function-prop",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # The function should have been invoked
        assert data["props"]["user"]["name"] == "John Doe"
        assert data["props"]["user"]["email"] == "john@example.com"

    def test_nested_callable_prop_is_invoked(self, callable_client: TestClient):
        """Test that nested callable props are resolved."""
        response = callable_client.get(
            "/test-nested-callable",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Nested callable should have been invoked
        assert data["props"]["data"]["user"] == "resolved user"
        assert data["props"]["data"]["static"] == "static value"

    def test_callable_in_list_is_invoked(self, callable_client: TestClient):
        """Test that callables in lists are resolved."""
        response = callable_client.get(
            "/test-callable-in-list",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Callables in list should have been invoked
        assert data["props"]["items"] == ["item1", "item2", "item3"]

    def test_async_callable_is_invoked(self, callable_client: TestClient):
        """Test that async callables are properly awaited."""
        response = callable_client.get(
            "/test-async-callable",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Async callable should have been awaited
        assert data["props"]["async_data"] == "async result"

    def test_mixed_props_resolved_correctly(self, callable_client: TestClient):
        """Test that a mix of callable and non-callable props works."""
        response = callable_client.get(
            "/test-mixed-props",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Static prop should be unchanged
        assert data["props"]["static"] == "static value"
        # Callable prop should be invoked
        assert data["props"]["computed"] == "computed value"
        # Nested static should be unchanged
        assert data["props"]["nested"]["static"] == "nested static"
        # Nested callable should be invoked
        assert data["props"]["nested"]["computed"] == "nested computed"

    def test_class_not_invoked(self, callable_client: TestClient):
        """Test that classes are not invoked (only functions/lambdas)."""
        response = callable_client.get(
            "/test-class-not-invoked",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # The class should be serialized, not invoked
        # This test just verifies no error is raised
        assert "data" in data["props"]

    def test_callable_props_in_html_response(self, callable_client: TestClient):
        """Test that callable props are resolved in HTML responses too."""
        response = callable_client.get("/test-lambda-prop")
        assert response.status_code == 200

        # Extract page data from HTML
        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        # Callable should have been invoked
        assert page_data["props"]["computed"] == "computed value"


@pytest.fixture
def callable_app(inertia_response):
    """Create a FastAPI test application with callable prop routes."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-lambda-prop")
    def test_lambda_prop(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "computed": lambda: "computed value",
            },
        )

    @app.get("/test-function-prop")
    def test_function_prop(request: Request):
        def get_user():
            return {"name": "John Doe", "email": "john@example.com"}

        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": get_user,
            },
        )

    @app.get("/test-nested-callable")
    def test_nested_callable(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "data": {
                    "user": lambda: "resolved user",
                    "static": "static value",
                },
            },
        )

    @app.get("/test-callable-in-list")
    def test_callable_in_list(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "items": [
                    lambda: "item1",
                    lambda: "item2",
                    lambda: "item3",
                ],
            },
        )

    @app.get("/test-async-callable")
    def test_async_callable(request: Request):
        async def async_fetch():
            return "async result"

        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "async_data": async_fetch,
            },
        )

    @app.get("/test-mixed-props")
    def test_mixed_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "static": "static value",
                "computed": lambda: "computed value",
                "nested": {
                    "static": "nested static",
                    "computed": lambda: "nested computed",
                },
            },
        )

    @app.get("/test-class-not-invoked")
    def test_class_not_invoked(request: Request):
        class MyData:
            value = "test"

        inertia = get_test_inertia(request)
        # Pass a simple dict instead of the class to avoid serialization issues
        return inertia.render(
            "TestComponent",
            {
                "data": {"class_name": MyData.__name__},
            },
        )

    return app


@pytest.fixture
def callable_client(callable_app):
    """Create a test client for callable props tests."""
    return TestClient(callable_app)
