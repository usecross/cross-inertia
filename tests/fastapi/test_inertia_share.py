from __future__ import annotations

import inspect
from datetime import date
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from httpx import Response

from cross_inertia.fastapi import inertia_share
from tests.page_html import extract_page_data

if TYPE_CHECKING:

    class MissingSharedData(dict[str, str]):
        pass


def get_test_user() -> str:
    return "alice"


def _provider_with_unresolvable_return(
    req: Request,
    since: date,
) -> MissingSharedData:
    return {"since": since.isoformat()}


def test_single_share_sets_data(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-single",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["auth"] == {"user": "alice"}
    assert data["props"]["title"] == "Hi"


def test_multiple_shares_merge(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-multiple",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["auth"] == {"user": "alice"}
    assert data["props"]["flash"] == {"msg": "saved"}


def test_async_share(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-async",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["async_key"] == 42


def test_sync_share(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-sync",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["sync_key"] == "hello"


def test_shared_data_in_html_response(share_client: TestClient) -> None:
    response: Response = share_client.get("/test-single")
    assert response.status_code == 200

    page_data: dict[str, Any] = extract_page_data(response.text)

    assert page_data["props"]["auth"] == {"user": "alice"}
    assert page_data["props"]["title"] == "Hi"


def test_auto_injects_request(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-no-request",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["count"] == 7


def test_auto_inject_with_other_deps(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-with-dep",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["count"] == 99


def test_sync_auto_inject(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-sync-no-request",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["sync_auto"] is True


def test_decorator_only(share_client: TestClient) -> None:
    response: Response = share_client.get(
        "/test-decorator-only",
        headers={"X-Inertia": "true"},
    )
    data: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert data["props"]["from_decorator"] is True


def test_share_accepts_postponed_request_annotation() -> None:
    def share(request: "Request") -> dict[str, bool]:
        return {"shared": True}

    wrapped = inertia_share(share)

    assert list(inspect.signature(wrapped).parameters) == ["request"]


def test_share_accepts_request_parameter_with_different_name() -> None:
    def share(req: Request) -> dict[str, bool]:
        return {"shared": bool(req)}

    wrapped = inertia_share(share)

    assert list(inspect.signature(wrapped).parameters) == ["req"]


def test_share_resolves_postponed_dependency_annotations(
    inertia_response,
) -> None:
    @inertia_share
    def share(
        request: Request,
        since: date,
        user: Annotated[str, Depends(get_test_user)],
    ) -> dict[str, str]:
        return {"since": since.isoformat(), "user": user}

    app = FastAPI(dependencies=[Depends(share)])

    @app.get("/")
    def index(request: Request):
        from cross_inertia._core import Inertia
        from cross_web import StarletteRequestAdapter

        inertia = Inertia(request, StarletteRequestAdapter(request), inertia_response)
        return inertia.render("Index", {})

    response = TestClient(app).get(
        "/?since=2026-08-02",
        headers={"X-Inertia": "true"},
    )

    assert response.status_code == 200
    assert response.json()["props"] == {
        "since": "2026-08-02",
        "user": "alice",
    }


def test_unresolved_return_does_not_poison_parameter_annotations() -> None:
    wrapped = inertia_share(_provider_with_unresolvable_return)
    parameters = inspect.signature(wrapped).parameters

    assert list(parameters) == ["req", "since"]
    assert parameters["req"].annotation is Request
    assert parameters["since"].annotation is date
