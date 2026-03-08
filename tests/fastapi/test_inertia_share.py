from typing import Any

from fastapi.testclient import TestClient
from httpx import Response

from tests.page_html import extract_page_data


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
