"""Tests for once props."""

import json

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from cross_web import StarletteRequestAdapter

from cross_inertia import defer, once
from cross_inertia._core import Inertia
from cross_inertia.fastapi import inertia_share


@inertia_share
async def share_reference_data():
    return {
        "countries": once(lambda: ["US", "SE"], key="countries-cache", until=60),
    }


@pytest.fixture
def once_app(inertia_response):
    app = FastAPI(dependencies=[Depends(share_reference_data)])

    def get_test_inertia(request: Request) -> Inertia:
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test-once")
    def test_once_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "plans": once(lambda: ["starter", "pro"], key="plans-cache", until=60),
                "permissions": once(
                    defer(lambda: ["invite"], group="sidebar"),
                    key="permissions-cache",
                ),
            },
        )

    return app


@pytest.fixture
def once_client(once_app: FastAPI):
    return TestClient(once_app)


class TestOnceProps:
    def test_initial_response_includes_props_and_once_metadata(
        self, once_client: TestClient
    ) -> None:
        response = once_client.get(
            "/test-once",
            headers={"X-Inertia": "true"},
        )

        data = response.json()
        assert data["props"]["plans"] == ["starter", "pro"]
        assert data["props"]["countries"] == ["US", "SE"]
        assert "permissions" not in data["props"]
        assert data["onceProps"]["plans-cache"]["prop"] == "plans"
        assert data["onceProps"]["countries-cache"]["prop"] == "countries"
        assert data["deferredProps"]["sidebar"] == ["permissions"]

    def test_remembered_once_props_are_omitted_from_non_partial_inertia_responses(
        self, once_client: TestClient
    ) -> None:
        response = once_client.get(
            "/test-once",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Except-Once-Props": "plans-cache,countries-cache,permissions-cache",
            },
        )

        data = response.json()
        assert "plans" not in data["props"]
        assert "countries" not in data["props"]
        assert "permissions" not in data["props"]
        assert "deferredProps" not in data
        assert set(data["onceProps"].keys()) == {
            "plans-cache",
            "countries-cache",
            "permissions-cache",
        }

    def test_partial_reload_refreshes_requested_once_props(
        self, once_client: TestClient
    ) -> None:
        response = once_client.get(
            "/test-once",
            headers={
                "X-Inertia": "true",
                "X-Inertia-Except-Once-Props": "plans-cache,countries-cache",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "plans,countries",
            },
        )

        data = response.json()
        assert data["props"]["plans"] == ["starter", "pro"]
        assert data["props"]["countries"] == ["US", "SE"]

    def test_html_response_includes_once_metadata(
        self, once_client: TestClient
    ) -> None:
        response = once_client.get("/test-once")

        html = response.text
        start = html.find("data-page='") + len("data-page='")
        end = html.find("'", start)
        page_data = json.loads(html[start:end])

        assert page_data["onceProps"]["plans-cache"]["prop"] == "plans"
        assert page_data["onceProps"]["permissions-cache"]["prop"] == "permissions"
