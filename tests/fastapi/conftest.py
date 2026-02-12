from typing import Any

import pytest
from cross_web import StarletteRequestAdapter
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response

from cross_inertia._core import Inertia, InertiaResponse
from cross_inertia.fastapi import inertia_share


@inertia_share
async def share_auth(request: Request) -> dict[str, Any]:
    return {"auth": {"user": "alice"}}


@inertia_share
async def share_flash(request: Request) -> dict[str, Any]:
    return {"flash": {"msg": "saved"}}


@inertia_share
async def share_async(request: Request) -> dict[str, Any]:
    return {"async_key": 42}


@inertia_share
def share_sync(request: Request) -> dict[str, Any]:
    return {"sync_key": "hello"}


@inertia_share
async def share_decorator_flag(request: Request) -> dict[str, Any]:
    return {"from_decorator": True}


def get_value() -> int:
    return 99


@inertia_share
async def share_no_request() -> dict[str, Any]:
    return {"count": 7}


@inertia_share
async def share_with_dep(value: int = Depends(get_value)) -> dict[str, Any]:
    return {"count": value}


@inertia_share
def share_sync_no_request() -> dict[str, Any]:
    return {"sync_auto": True}


@pytest.fixture
def share_app(inertia_response: InertiaResponse) -> FastAPI:
    app = FastAPI(
        dependencies=[
            Depends(share_auth),
            Depends(share_flash),
            Depends(share_async),
            Depends(share_sync),
            Depends(share_decorator_flag),
        ]
    )

    def get_test_inertia(request: Request) -> Inertia:
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-single")
    def test_single(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {"title": "Hi"})

    @app.get("/test-multiple")
    def test_multiple(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-async")
    def test_async(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-sync")
    def test_sync(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-no-request", dependencies=[Depends(share_no_request)])
    def test_no_request(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-with-dep", dependencies=[Depends(share_with_dep)])
    def test_with_dep(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-sync-no-request", dependencies=[Depends(share_sync_no_request)])
    def test_sync_no_request(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    @app.get("/test-decorator-only")
    def test_decorator_only(request: Request) -> Response:
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {})

    return app


@pytest.fixture
def share_client(share_app: FastAPI) -> TestClient:
    return TestClient(share_app)
