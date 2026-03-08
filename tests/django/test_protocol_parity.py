"""Cross-framework parity tests for the shared page builder."""

from datetime import datetime, timezone

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from cross_web import StarletteRequestAdapter

from cross_inertia import defer, once, optional
from cross_inertia._core import Inertia
from cross_inertia.fastapi import inertia_share

FIXED_ONCE_EXPIRY = datetime(2030, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def setup_inertia(django_inertia_response):
    """Set up and tear down Django Inertia response singleton for tests."""
    from cross_inertia.django.shortcuts import reset_inertia_response
    import cross_inertia.django.shortcuts as shortcuts

    shortcuts._inertia_response = django_inertia_response
    yield
    reset_inertia_response()


@inertia_share
async def share_data():
    return {
        "auth": {"user": "alice"},
        "flash": {"msg": "saved"},
    }


@pytest.fixture
def fastapi_parity_client(inertia_response):
    app = FastAPI(dependencies=[Depends(share_data)])

    def get_test_inertia(request: Request) -> Inertia:
        adapter = StarletteRequestAdapter(request)
        return Inertia(request, adapter, inertia_response)

    @app.get("/test/")
    def test_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render("TestComponent", {"message": "Hello, World!"})

    @app.get("/nested-props/")
    def nested_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "profile": {
                    "name": "John",
                    "email": "john@example.com",
                    "permissions": optional(lambda: ["invite"]),
                },
                "stats": {
                    "count": 42,
                    "items": ["a", "b"],
                },
            },
        )

    @app.get("/deferred-props/")
    def deferred_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "user": "John",
                "analytics": defer(lambda: {"views": 1000}, group="default"),
            },
        )

    @app.get("/once-props/")
    def once_props(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "plans": once(
                    lambda: ["starter", "pro"],
                    key="plans-cache",
                    until=FIXED_ONCE_EXPIRY,
                ),
                "permissions": once(
                    defer(lambda: ["invite"], group="sidebar"),
                    key="permissions-cache",
                ),
            },
        )

    @app.get("/reset/")
    def reset_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {
                "users": [{"id": 1, "name": "User"}],
                "filters": {"role": "admin"},
            },
            merge_props=["users"],
        )

    @app.get("/history/")
    def history_route(request: Request):
        inertia = get_test_inertia(request)
        inertia.encrypt_history().clear_history()
        return inertia.render("TestComponent", {"message": "History"})

    @app.get("/with-errors/")
    def errors_route(request: Request):
        inertia = get_test_inertia(request)
        return inertia.render(
            "TestComponent",
            {"message": "Hello"},
            errors={"field": "This field is required"},
        )

    return TestClient(app)


def test_basic_page_and_shared_data_match(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_response = fastapi_parity_client.get(
        "/test/", headers={"X-Inertia": "true"}
    )
    django_response = client.get("/test/", HTTP_X_INERTIA="true")

    assert fastapi_response.json() == django_response.json()


def test_nested_partial_reload_match(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_response = fastapi_parity_client.get(
        "/nested-props/",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Component": "TestComponent",
            "X-Inertia-Partial-Data": "profile,stats",
            "X-Inertia-Partial-Except": "profile.email",
        },
    )
    django_response = client.get(
        "/nested-props/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        HTTP_X_INERTIA_PARTIAL_DATA="profile,stats",
        HTTP_X_INERTIA_PARTIAL_EXCEPT="profile.email",
    )

    assert fastapi_response.json() == django_response.json()


def test_deferred_props_match_on_initial_and_partial_requests(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_initial = fastapi_parity_client.get(
        "/deferred-props/",
        headers={"X-Inertia": "true"},
    )
    django_initial = client.get("/deferred-props/", HTTP_X_INERTIA="true")
    assert fastapi_initial.json() == django_initial.json()

    fastapi_partial = fastapi_parity_client.get(
        "/deferred-props/",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Component": "TestComponent",
            "X-Inertia-Partial-Data": "analytics",
        },
    )
    django_partial = client.get(
        "/deferred-props/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_PARTIAL_COMPONENT="TestComponent",
        HTTP_X_INERTIA_PARTIAL_DATA="analytics",
    )
    assert fastapi_partial.json() == django_partial.json()


def test_once_props_match_on_initial_and_remembered_requests(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_initial = fastapi_parity_client.get(
        "/once-props/",
        headers={"X-Inertia": "true"},
    )
    django_initial = client.get("/once-props/", HTTP_X_INERTIA="true")
    assert fastapi_initial.json() == django_initial.json()

    fastapi_remembered = fastapi_parity_client.get(
        "/once-props/",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Except-Once-Props": "plans-cache,permissions-cache",
        },
    )
    django_remembered = client.get(
        "/once-props/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_EXCEPT_ONCE_PROPS="plans-cache,permissions-cache",
    )
    assert fastapi_remembered.json() == django_remembered.json()


def test_reset_metadata_matches(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_response = fastapi_parity_client.get(
        "/reset/",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Reset": "users",
        },
    )
    django_response = client.get(
        "/reset/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_RESET="users",
    )

    assert fastapi_response.json() == django_response.json()


def test_history_flags_match(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_response = fastapi_parity_client.get(
        "/history/",
        headers={"X-Inertia": "true"},
    )
    django_response = client.get("/history/", HTTP_X_INERTIA="true")

    assert fastapi_response.json() == django_response.json()


def test_validation_errors_and_error_bags_match(
    fastapi_parity_client: TestClient,
    client,
    setup_inertia,
):
    fastapi_response = fastapi_parity_client.get(
        "/with-errors/",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Error-Bag": "login",
        },
    )
    django_response = client.get(
        "/with-errors/",
        HTTP_X_INERTIA="true",
        HTTP_X_INERTIA_ERROR_BAG="login",
    )

    assert fastapi_response.json() == django_response.json()
