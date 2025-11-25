"""Tests for lazy/optional/always props functionality."""

import json

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from inertia import lazy, optional, always


class TestLazyProps:
    """Test that lazy props are only included when explicitly requested."""

    def test_lazy_prop_excluded_on_initial_load(self, lazy_client: TestClient):
        """Test that lazy props are NOT included on initial page load."""
        response = lazy_client.get(
            "/test-lazy",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Regular prop should be included
        assert data["props"]["user"] == "John"
        # Lazy prop should NOT be included
        assert "permissions" not in data["props"]

    def test_lazy_prop_included_on_partial_reload(self, lazy_client: TestClient):
        """Test that lazy props ARE included when explicitly requested."""
        response = lazy_client.get(
            "/test-lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "permissions",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Lazy prop should be included and evaluated
        assert data["props"]["permissions"] == ["read", "write"]

    def test_lazy_prop_with_args(self, lazy_client: TestClient):
        """Test lazy props with positional arguments (like functools.partial)."""
        response = lazy_client.get(
            "/test-lazy-with-args",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user_data",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["user_data"]["id"] == 123
        assert data["props"]["user_data"]["name"] == "Test User"

    def test_lazy_prop_with_kwargs(self, lazy_client: TestClient):
        """Test lazy props with keyword arguments."""
        response = lazy_client.get(
            "/test-lazy-with-kwargs",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "activity",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert len(data["props"]["activity"]) == 10  # limit=10

    def test_multiple_lazy_props(self, lazy_client: TestClient):
        """Test requesting multiple lazy props at once."""
        response = lazy_client.get(
            "/test-multiple-lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "permissions,billing",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["permissions"] == ["admin"]
        assert data["props"]["billing"]["plan"] == "pro"

    def test_mixed_regular_and_lazy_props(self, lazy_client: TestClient):
        """Test that regular props work alongside lazy props on partial reload."""
        response = lazy_client.get(
            "/test-lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user,permissions",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Both should be included
        assert data["props"]["user"] == "John"
        assert data["props"]["permissions"] == ["read", "write"]

    def test_lazy_prop_excluded_with_except_header(self, lazy_client: TestClient):
        """Test that lazy props are excluded even with except header."""
        response = lazy_client.get(
            "/test-lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Except": "nothing",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Regular prop should be included
        assert data["props"]["user"] == "John"
        # Lazy prop should still be excluded
        assert "permissions" not in data["props"]

    def test_lazy_prop_in_html_response(self, lazy_client: TestClient):
        """Test that lazy props are excluded from HTML responses too."""
        response = lazy_client.get("/test-lazy")
        assert response.status_code == 200

        # Extract page data from HTML
        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        # Regular prop should be there
        assert page_data["props"]["user"] == "John"
        # Lazy prop should not be there
        assert "permissions" not in page_data["props"]

    def test_async_lazy_prop(self, lazy_client: TestClient):
        """Test that async lazy props are properly awaited."""
        response = lazy_client.get(
            "/test-async-lazy",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "async_data",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["async_data"] == "async result"


class TestLazyPropValidation:
    """Test LazyProp validation and edge cases."""

    def test_lazy_requires_callable(self):
        """Test that lazy() raises error for non-callable."""
        with pytest.raises(ValueError, match="requires a callable"):
            lazy("not a callable")

    def test_lazy_with_no_args(self):
        """Test lazy() with just a callable, no args."""

        def get_data():
            return "data"

        prop = lazy(get_data)
        assert prop() == "data"

    def test_lazy_with_positional_args(self):
        """Test lazy() with positional args like partial()."""

        def get_user(user_id, include_email):
            return {"id": user_id, "include_email": include_email}

        prop = lazy(get_user, 123, True)
        result = prop()
        assert result["id"] == 123
        assert result["include_email"] is True

    def test_lazy_with_kwargs(self):
        """Test lazy() with keyword args like partial()."""

        def get_items(category, limit=10, offset=0):
            return {"category": category, "limit": limit, "offset": offset}

        prop = lazy(get_items, "books", limit=5, offset=10)
        result = prop()
        assert result["category"] == "books"
        assert result["limit"] == 5
        assert result["offset"] == 10


@pytest.fixture
def lazy_app(inertia_response):
    """Create a FastAPI test application with lazy prop routes."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def get_permissions():
        return ["read", "write"]

    def get_user_by_id(user_id: int):
        return {"id": user_id, "name": "Test User"}

    def get_activity(user_id: int, limit: int = 50):
        return [{"action": f"action_{i}"} for i in range(limit)]

    async def async_fetch():
        return "async result"

    @app.get("/test-lazy")
    def test_lazy(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",
                "permissions": lazy(get_permissions),
            },
        )

    @app.get("/test-lazy-with-args")
    def test_lazy_with_args(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user_data": lazy(get_user_by_id, 123),
            },
        )

    @app.get("/test-lazy-with-kwargs")
    def test_lazy_with_kwargs(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "activity": lazy(get_activity, user_id=1, limit=10),
            },
        )

    @app.get("/test-multiple-lazy")
    def test_multiple_lazy(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "Jane",
                "permissions": lazy(lambda: ["admin"]),
                "billing": lazy(lambda: {"plan": "pro"}),
            },
        )

    @app.get("/test-async-lazy")
    def test_async_lazy(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "async_data": lazy(async_fetch),
            },
        )

    return app


@pytest.fixture
def lazy_client(lazy_app):
    """Create a test client for lazy props tests."""
    return TestClient(lazy_app)


class TestOptionalProps:
    """Test that optional() is an alias for lazy() and works the same way."""

    def test_optional_is_alias_for_lazy(self):
        """Test that optional is the same class as lazy."""
        assert optional is lazy

    def test_optional_prop_excluded_on_initial_load(self, optional_client: TestClient):
        """Test that optional props are NOT included on initial page load."""
        response = optional_client.get(
            "/test-optional",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Regular prop should be included
        assert data["props"]["user"] == "John"
        # Optional prop should NOT be included
        assert "permissions" not in data["props"]

    def test_optional_prop_included_on_partial_reload(
        self, optional_client: TestClient
    ):
        """Test that optional props ARE included when explicitly requested."""
        response = optional_client.get(
            "/test-optional",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "permissions",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Optional prop should be included and evaluated
        assert data["props"]["permissions"] == ["read", "write"]


class TestAlwaysProps:
    """Test that always() props are always included, even during partial reloads."""

    def test_always_prop_included_on_initial_load(self, always_client: TestClient):
        """Test that always props ARE included on initial page load."""
        response = always_client.get(
            "/test-always",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["user"] == "John"
        assert data["props"]["flash"] == {"message": "Welcome!"}

    def test_always_prop_included_on_partial_reload(self, always_client: TestClient):
        """Test that always props ARE included even when not requested."""
        response = always_client.get(
            "/test-always",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user",  # Only request user, not flash
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Both should be included even though we only requested "user"
        assert data["props"]["user"] == "John"
        assert data["props"]["flash"] == {"message": "Welcome!"}

    def test_always_prop_not_excluded_with_except_header(
        self, always_client: TestClient
    ):
        """Test that always props cannot be excluded with except header."""
        response = always_client.get(
            "/test-always",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Except": "flash",  # Try to exclude flash
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Flash should STILL be included even though we tried to exclude it
        assert data["props"]["user"] == "John"
        assert data["props"]["flash"] == {"message": "Welcome!"}

    def test_always_with_callable(self, always_client: TestClient):
        """Test that always() works with callables."""
        response = always_client.get(
            "/test-always-callable",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Callable always prop should be evaluated
        assert data["props"]["notifications"] == ["notif1", "notif2"]

    def test_always_with_static_value(self, always_client: TestClient):
        """Test that always() works with static values."""
        response = always_client.get(
            "/test-always-static",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Static always prop should be passed through
        assert data["props"]["version"] == "1.0.0"


class TestAlwaysPropValidation:
    """Test always prop validation and edge cases."""

    def test_always_with_static_value(self):
        """Test always() with a static value."""
        prop = always("static")
        assert prop() == "static"

    def test_always_with_callable(self):
        """Test always() with a callable."""

        def get_data():
            return "from callable"

        prop = always(get_data)
        assert prop() == "from callable"

    def test_always_with_args(self):
        """Test always() with callable and args."""

        def get_user(user_id):
            return {"id": user_id}

        prop = always(get_user, 123)
        assert prop()["id"] == 123

    def test_always_with_kwargs(self):
        """Test always() with callable and kwargs."""

        def get_items(limit=10):
            return list(range(limit))

        prop = always(get_items, limit=5)
        assert len(prop()) == 5


class TestMixedPropTypes:
    """Test combinations of optional, always, and regular props."""

    def test_mixed_optional_always_regular(self, mixed_client: TestClient):
        """Test that all prop types work together correctly."""
        # Initial load - optional excluded, always and regular included
        response = mixed_client.get(
            "/test-mixed",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["user"] == "John"  # regular
        assert data["props"]["flash"] == {"type": "success"}  # always
        assert "expensive_data" not in data["props"]  # optional excluded

    def test_mixed_partial_reload_includes_always(self, mixed_client: TestClient):
        """Test that always props are included during partial reload."""
        response = mixed_client.get(
            "/test-mixed",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "expensive_data",  # Only request optional
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Optional should now be included (explicitly requested)
        assert data["props"]["expensive_data"] == {"computed": True}
        # Always should still be included
        assert data["props"]["flash"] == {"type": "success"}
        # User not requested, so not included
        assert "user" not in data["props"]


@pytest.fixture
def optional_app(inertia_response):
    """Create a FastAPI test application with optional prop routes."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def get_permissions():
        return ["read", "write"]

    @app.get("/test-optional")
    def test_optional(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",
                "permissions": optional(get_permissions),
            },
        )

    return app


@pytest.fixture
def optional_client(optional_app):
    """Create a test client for optional props tests."""
    return TestClient(optional_app)


@pytest.fixture
def always_app(inertia_response):
    """Create a FastAPI test application with always prop routes."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def get_notifications():
        return ["notif1", "notif2"]

    @app.get("/test-always")
    def test_always(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",
                "flash": always({"message": "Welcome!"}),
            },
        )

    @app.get("/test-always-callable")
    def test_always_callable(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "Jane",
                "notifications": always(get_notifications),
            },
        )

    @app.get("/test-always-static")
    def test_always_static(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "Jane",
                "version": always("1.0.0"),
            },
        )

    return app


@pytest.fixture
def always_client(always_app):
    """Create a test client for always props tests."""
    return TestClient(always_app)


@pytest.fixture
def mixed_app(inertia_response):
    """Create a FastAPI test application with mixed prop types."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def compute_expensive():
        return {"computed": True}

    @app.get("/test-mixed")
    def test_mixed(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",  # Regular prop
                "flash": always({"type": "success"}),  # Always prop
                "expensive_data": optional(compute_expensive),  # Optional prop
            },
        )

    return app


@pytest.fixture
def mixed_client(mixed_app):
    """Create a test client for mixed props tests."""
    return TestClient(mixed_app)
