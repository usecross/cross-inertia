"""Tests for the @inertia_share decorator."""

import json

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from cross_inertia.fastapi import InertiaMiddleware, inertia_share


class TestInertiaShare:
    """Test that @inertia_share sets shared data on requests."""

    def test_single_share_sets_data(self, share_client: TestClient):
        response = share_client.get(
            "/test-single",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["auth"] == {"user": "alice"}
        assert data["props"]["title"] == "Hi"

    def test_multiple_shares_merge(self, share_client: TestClient):
        response = share_client.get(
            "/test-multiple",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["auth"] == {"user": "alice"}
        assert data["props"]["flash"] == {"msg": "saved"}

    def test_async_share(self, share_client: TestClient):
        response = share_client.get(
            "/test-async",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["async_key"] == 42

    def test_sync_share(self, share_client: TestClient):
        response = share_client.get(
            "/test-sync",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["sync_key"] == "hello"

    def test_shared_data_in_html_response(self, share_client: TestClient):
        response = share_client.get("/test-single")
        assert response.status_code == 200

        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_data = json.loads(html[start:end])

        assert page_data["props"]["auth"] == {"user": "alice"}
        assert page_data["props"]["title"] == "Hi"


class TestInertiaShareAutoInject:
    """Test that request is auto-injected when not in the function signature."""

    def test_auto_injects_request(self, auto_inject_client: TestClient):
        response = auto_inject_client.get(
            "/test-no-request",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["count"] == 7

    def test_auto_inject_with_other_deps(self, auto_inject_client: TestClient):
        response = auto_inject_client.get(
            "/test-with-dep",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["count"] == 99

    def test_sync_auto_inject(self, auto_inject_client: TestClient):
        response = auto_inject_client.get(
            "/test-sync-no-request",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["sync_auto"] is True


class TestInertiaShareWithMiddleware:
    """Test that @inertia_share works alongside InertiaMiddleware."""

    def test_middleware_without_share(self, middleware_client: TestClient):
        response = middleware_client.get(
            "/test-decorator-only",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["from_decorator"] is True

    def test_middleware_with_share_plus_decorator(
        self, middleware_with_share_client: TestClient
    ):
        response = middleware_with_share_client.get(
            "/test-both",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert data["props"]["from_middleware"] is True
        assert data["props"]["from_decorator"] is True


# --- Fixtures ---


@pytest.fixture
def share_app(inertia_response):
    from cross_inertia._core import Inertia
    from cross_web import StarletteRequestAdapter

    @inertia_share
    async def share_auth(request: Request):
        return {"auth": {"user": "alice"}}

    @inertia_share
    async def share_flash(request: Request):
        return {"flash": {"msg": "saved"}}

    @inertia_share
    async def share_async(request: Request):
        return {"async_key": 42}

    @inertia_share
    def share_sync(request: Request):
        return {"sync_key": "hello"}

    app = FastAPI(
        dependencies=[
            Depends(share_auth),
            Depends(share_flash),
            Depends(share_async),
            Depends(share_sync),
        ]
    )
    app.add_middleware(InertiaMiddleware)

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-single")
    def test_single(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {"title": "Hi"})

    @app.get("/test-multiple")
    def test_multiple(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-async")
    def test_async(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-sync")
    def test_sync(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    return app


@pytest.fixture
def share_client(share_app):
    return TestClient(share_app)


@pytest.fixture
def auto_inject_app(inertia_response):
    from cross_inertia._core import Inertia
    from cross_web import StarletteRequestAdapter

    def get_value():
        return 99

    @inertia_share
    async def share_no_request():
        return {"count": 7}

    @inertia_share
    async def share_with_dep(value: int = Depends(get_value)):
        return {"count": value}

    @inertia_share
    def share_sync_no_request():
        return {"sync_auto": True}

    app = FastAPI()
    app.add_middleware(InertiaMiddleware)

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-no-request", dependencies=[Depends(share_no_request)])
    def test_no_request(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-with-dep", dependencies=[Depends(share_with_dep)])
    def test_with_dep(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-sync-no-request", dependencies=[Depends(share_sync_no_request)])
    def test_sync_no_request(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    return app


@pytest.fixture
def auto_inject_client(auto_inject_app):
    return TestClient(auto_inject_app)


@pytest.fixture
def middleware_app(inertia_response):
    from cross_inertia._core import Inertia
    from cross_web import StarletteRequestAdapter

    @inertia_share
    async def share_data(request: Request):
        return {"from_decorator": True}

    app = FastAPI(dependencies=[Depends(share_data)])
    app.add_middleware(InertiaMiddleware)

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-decorator-only")
    def test_decorator_only(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    return app


@pytest.fixture
def middleware_client(middleware_app):
    return TestClient(middleware_app)


@pytest.fixture
def middleware_with_share_app(inertia_response):
    from cross_inertia._core import Inertia
    from cross_web import StarletteRequestAdapter

    def middleware_share(request: Request):
        return {"from_middleware": True}

    @inertia_share
    async def share_extra(request: Request):
        return {"from_decorator": True}

    app = FastAPI(dependencies=[Depends(share_extra)])
    app.add_middleware(InertiaMiddleware, share=middleware_share)

    def get_test_inertia(request: Request):
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-both")
    def test_both(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    return app


@pytest.fixture
def middleware_with_share_client(middleware_with_share_app):
    return TestClient(middleware_with_share_app)
