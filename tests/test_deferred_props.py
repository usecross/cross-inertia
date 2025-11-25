"""Tests for deferred props functionality."""

import json

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from inertia import defer


class TestDeferredPropsCore:
    """Test that deferred props are excluded on initial load with deferredProps metadata."""

    def test_deferred_prop_excluded_on_initial_load(
        self, deferred_core_client: TestClient
    ):
        """Test that deferred props are NOT included in props on initial page load."""
        response = deferred_core_client.get(
            "/test-deferred",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Regular prop should be included
        assert data["props"]["user"] == "John"
        # Deferred prop should NOT be in props
        assert "analytics" not in data["props"]

    def test_deferred_props_map_in_response(self, deferred_core_client: TestClient):
        """Test that deferredProps map is included in response."""
        response = deferred_core_client.get(
            "/test-deferred",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # deferredProps should be present
        assert "deferredProps" in data
        # analytics should be in the default group
        assert "default" in data["deferredProps"]
        assert "analytics" in data["deferredProps"]["default"]

    def test_deferred_prop_included_on_partial_reload(
        self, deferred_core_client: TestClient
    ):
        """Test that deferred props ARE resolved when explicitly requested."""
        response = deferred_core_client.get(
            "/test-deferred",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "analytics",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Deferred prop should be included and evaluated
        assert data["props"]["analytics"] == {"views": 1000, "visitors": 500}
        # deferredProps should NOT be in partial reload response
        assert "deferredProps" not in data

    def test_deferred_prop_with_args(self, deferred_core_client: TestClient):
        """Test deferred props with positional arguments."""
        response = deferred_core_client.get(
            "/test-deferred-with-args",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "user_stats",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["user_stats"]["user_id"] == 123
        assert data["props"]["user_stats"]["stats"] == {"posts": 10}

    def test_deferred_prop_with_kwargs(self, deferred_core_client: TestClient):
        """Test deferred props with keyword arguments."""
        response = deferred_core_client.get(
            "/test-deferred-with-kwargs",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "report",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert len(data["props"]["report"]) == 10  # limit=10

    def test_deferred_props_grouping(self, deferred_core_client: TestClient):
        """Test that deferred props are grouped correctly."""
        response = deferred_core_client.get(
            "/test-deferred-groups",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        # Check groups
        assert "deferredProps" in data
        assert "default" in data["deferredProps"]
        assert "analytics" in data["deferredProps"]["default"]
        assert "notifications" in data["deferredProps"]["default"]
        assert "sidebar" in data["deferredProps"]
        assert "recommendations" in data["deferredProps"]["sidebar"]

    def test_multiple_deferred_props_same_group(self, deferred_core_client: TestClient):
        """Test requesting multiple deferred props from the same group."""
        response = deferred_core_client.get(
            "/test-deferred-groups",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "analytics,notifications",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["analytics"] == {"pageviews": 5000}
        assert data["props"]["notifications"] == [{"id": 1, "msg": "Hello"}]

    def test_deferred_props_excluded_with_except_header(
        self, deferred_core_client: TestClient
    ):
        """Test that deferred props are excluded with except header."""
        response = deferred_core_client.get(
            "/test-deferred",
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
        # Deferred prop should still be excluded
        assert "analytics" not in data["props"]

    def test_deferred_prop_in_html_response(self, deferred_core_client: TestClient):
        """Test that deferred props are excluded from HTML responses with deferredProps."""
        response = deferred_core_client.get("/test-deferred")
        assert response.status_code == 200

        # Extract page data from HTML
        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_json = html[start:end]
        page_data = json.loads(page_json)

        # Regular prop should be there
        assert page_data["props"]["user"] == "John"
        # Deferred prop should not be in props
        assert "analytics" not in page_data["props"]
        # deferredProps should be present
        assert "deferredProps" in page_data
        assert "analytics" in page_data["deferredProps"]["default"]

    def test_async_deferred_prop(self, deferred_core_client: TestClient):
        """Test that async deferred props are properly awaited."""
        response = deferred_core_client.get(
            "/test-async-deferred",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "async_data",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["async_data"] == "async result"


class TestDeferredPropValidation:
    """Test deferred prop validation and edge cases."""

    def test_defer_requires_callable(self):
        """Test that defer() raises error for non-callable."""
        with pytest.raises(ValueError, match="requires a callable"):
            defer("not a callable")

    def test_defer_with_no_args(self):
        """Test defer() with just a callable, no args."""

        def get_data():
            return "data"

        prop = defer(get_data)
        assert prop() == "data"
        assert prop.group == "default"

    def test_defer_with_positional_args(self):
        """Test defer() with positional args like partial()."""

        def get_user_stats(user_id, include_history):
            return {"id": user_id, "include_history": include_history}

        prop = defer(get_user_stats, 123, True)
        result = prop()
        assert result["id"] == 123
        assert result["include_history"] is True
        assert prop.group == "default"

    def test_defer_with_kwargs(self):
        """Test defer() with keyword args like partial()."""

        def get_items(category, limit=10, offset=0):
            return {"category": category, "limit": limit, "offset": offset}

        prop = defer(get_items, "books", limit=5, offset=10)
        result = prop()
        assert result["category"] == "books"
        assert result["limit"] == 5
        assert result["offset"] == 10

    def test_defer_with_custom_group(self):
        """Test defer() with custom group name."""

        def get_data():
            return "data"

        prop = defer(get_data, group="sidebar")
        assert prop.group == "sidebar"
        assert prop() == "data"

    def test_defer_with_args_and_custom_group(self):
        """Test defer() with args and custom group."""

        def get_items(category):
            return {"category": category}

        prop = defer(get_items, "electronics", group="products")
        assert prop.group == "products"
        assert prop()["category"] == "electronics"


class TestMixedDeferredProps:
    """Test combinations of deferred, optional, always, and regular props."""

    def test_mixed_deferred_optional_always_regular(
        self, mixed_deferred_client: TestClient
    ):
        """Test that all prop types work together correctly."""
        # Initial load - deferred and optional excluded, always and regular included
        response = mixed_deferred_client.get(
            "/test-mixed-all",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["user"] == "John"  # regular
        assert data["props"]["flash"] == {"type": "success"}  # always
        assert "expensive_data" not in data["props"]  # optional excluded
        assert "analytics" not in data["props"]  # deferred excluded
        # deferredProps should be present
        assert "deferredProps" in data
        assert "analytics" in data["deferredProps"]["default"]

    def test_mixed_partial_reload_with_deferred(
        self, mixed_deferred_client: TestClient
    ):
        """Test partial reload with deferred prop."""
        response = mixed_deferred_client.get(
            "/test-mixed-all",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "analytics",
            },
        )
        data = response.json()

        assert response.status_code == 200
        # Deferred should now be included (explicitly requested)
        assert data["props"]["analytics"] == {"computed": True}
        # Always should still be included
        assert data["props"]["flash"] == {"type": "success"}
        # User not requested, so not included
        assert "user" not in data["props"]
        # deferredProps should NOT be in partial reload
        assert "deferredProps" not in data


@pytest.fixture
def deferred_core_app(inertia_response):
    """Create a FastAPI test application with deferred prop routes."""
    from inertia._core import Inertia
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def get_analytics():
        return {"views": 1000, "visitors": 500}

    def get_user_stats(user_id: int):
        return {"user_id": user_id, "stats": {"posts": 10}}

    def get_report(user_id: int, limit: int = 50):
        return [{"report": f"report_{i}"} for i in range(limit)]

    def get_pageviews():
        return {"pageviews": 5000}

    def get_notifications():
        return [{"id": 1, "msg": "Hello"}]

    def get_recommendations():
        return [{"id": 1, "title": "Item 1"}]

    async def async_fetch():
        return "async result"

    @app.get("/test-deferred")
    def test_deferred(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",
                "analytics": defer(get_analytics),
            },
        )

    @app.get("/test-deferred-with-args")
    def test_deferred_with_args(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user_stats": defer(get_user_stats, 123),
            },
        )

    @app.get("/test-deferred-with-kwargs")
    def test_deferred_with_kwargs(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "report": defer(get_report, user_id=1, limit=10),
            },
        )

    @app.get("/test-deferred-groups")
    def test_deferred_groups(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "Jane",
                "analytics": defer(get_pageviews),  # default group
                "notifications": defer(get_notifications),  # default group
                "recommendations": defer(get_recommendations, group="sidebar"),
            },
        )

    @app.get("/test-async-deferred")
    def test_async_deferred(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "async_data": defer(async_fetch),
            },
        )

    return app


@pytest.fixture
def deferred_core_client(deferred_core_app):
    """Create a test client for deferred props tests."""
    return TestClient(deferred_core_app)


@pytest.fixture
def mixed_deferred_app(inertia_response):
    """Create a FastAPI test application with mixed prop types including deferred."""
    from inertia._core import Inertia
    from inertia import optional, always
    from lia import StarletteRequestAdapter

    app = FastAPI()

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    def compute_expensive():
        return {"computed": True}

    def get_analytics():
        return {"computed": True}

    @app.get("/test-mixed-all")
    def test_mixed_all(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",  # Regular prop
                "flash": always({"type": "success"}),  # Always prop
                "expensive_data": optional(compute_expensive),  # Optional prop
                "analytics": defer(get_analytics),  # Deferred prop
            },
        )

    return app


@pytest.fixture
def mixed_deferred_client(mixed_deferred_app):
    """Create a test client for mixed deferred props tests."""
    return TestClient(mixed_deferred_app)
