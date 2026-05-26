from __future__ import annotations

from typing import Annotated, Any

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, model_validator
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from cross_inertia._core import InertiaResponse
from cross_inertia.fastapi import (
    InertiaDep,
    get_inertia_response,
    inertia_exception_handlers,
)
from cross_inertia.fastapi.validation import (
    pop_validation_errors_from_session,
    validation_errors_from_exception,
)


class ConferenceForm(BaseModel):
    name: str
    start_date: str
    end_date: str

    @model_validator(mode="after")
    def end_date_after_start_date(self) -> "ConferenceForm":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


def create_validation_app(inertia_response: InertiaResponse) -> FastAPI:
    app = FastAPI(exception_handlers=inertia_exception_handlers())
    app.add_middleware(SessionMiddleware, secret_key="test-secret")
    app.dependency_overrides[get_inertia_response] = lambda: inertia_response

    @app.get("/users/create")
    def create_user(inertia: InertiaDep) -> Response:
        return inertia.render("Users/Create", {"title": "Create user"})

    @app.post("/users")
    def store_user(
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
    ) -> RedirectResponse:
        return RedirectResponse("/users", status_code=303)

    @app.get("/conferences/1/edit")
    def edit_conference(inertia: InertiaDep) -> Response:
        return inertia.render(
            "Conferences/Edit",
            {
                "conference": {
                    "id": 1,
                    "name": "PyCon Italia",
                    "start_date": "2026-05-28",
                    "end_date": "2026-05-31",
                }
            },
        )

    @app.patch("/conferences/1")
    def update_conference(data: ConferenceForm) -> RedirectResponse:
        return RedirectResponse("/conferences", status_code=303)

    @app.get("/search")
    def search(page: int) -> dict[str, int]:
        return {"page": page}

    return app


def create_direct_render_app(inertia_response: InertiaResponse) -> FastAPI:
    from cross_web import StarletteRequestAdapter

    app = FastAPI(exception_handlers=inertia_exception_handlers())
    app.add_middleware(SessionMiddleware, secret_key="test-secret")

    @app.get("/users/create")
    def create_user(request: Request) -> Response:
        adapter = StarletteRequestAdapter(request)
        return inertia_response.render(
            request,
            adapter,
            "Users/Create",
            {"title": "Create user"},
        )

    @app.post("/users")
    def store_user(
        name: Annotated[str, Form()],
        email: Annotated[str, Form()],
    ) -> RedirectResponse:
        return RedirectResponse("/users", status_code=303)

    return app


def test_fastapi_validation_errors_redirect_back_and_store_to_errors_prop(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.post(
        "/users",
        headers={
            "X-Inertia": "true",
            "Referer": "http://testserver/users/create",
        },
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/users/create"

    redirected = client.get("/users/create", headers={"X-Inertia": "true"})
    data: dict[str, Any] = redirected.json()

    assert redirected.status_code == 200
    assert data["props"]["errors"]["name"] == "Field required"

    next_visit = client.get("/users/create", headers={"X-Inertia": "true"})
    assert "errors" not in next_visit.json()["props"]


def test_fastapi_validation_errors_redirect_to_previous_inertia_page_without_referer(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    client.get("/users/create?tab=profile", headers={"X-Inertia": "true"})

    response = client.post(
        "/users",
        headers={"X-Inertia": "true"},
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/users/create?tab=profile"


def test_fastapi_validation_errors_redirect_to_root_without_referer_or_previous_url(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.post(
        "/users",
        headers={"X-Inertia": "true"},
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_fastapi_validation_errors_are_scoped_to_inertia_dependency(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_direct_render_app(inertia_response))

    response = client.post(
        "/users",
        headers={
            "X-Inertia": "true",
            "Referer": "http://testserver/users/create",
        },
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 303

    redirected = client.get("/users/create", headers={"X-Inertia": "true"})
    assert "errors" not in redirected.json()["props"]


def test_fastapi_validation_errors_respect_error_bag(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.post(
        "/users",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Error-Bag": "createUser",
            "Referer": "http://testserver/users/create",
        },
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 303

    redirected = client.get("/users/create", headers={"X-Inertia": "true"})
    data: dict[str, Any] = redirected.json()

    assert data["props"]["errors"]["createUser"]["name"] == "Field required"


def test_fastapi_model_validation_errors_use_non_field_key_without_value_error_prefix(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.patch(
        "/conferences/1",
        headers={
            "X-Inertia": "true",
            "Referer": "http://testserver/conferences/1/edit",
        },
        json={
            "name": "PyCon Italia",
            "start_date": "2026-06-01",
            "end_date": "2026-05-29",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    redirected = client.get("/conferences/1/edit", headers={"X-Inertia": "true"})
    data: dict[str, Any] = redirected.json()

    assert data["props"]["errors"]["_form"] == "end_date must be after start_date"


def test_non_inertia_validation_errors_keep_fastapi_default_response(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.post(
        "/users",
        data={"email": "patrick@example.com"},
        follow_redirects=False,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_get_validation_errors_keep_fastapi_default_response(
    inertia_response: InertiaResponse,
) -> None:
    client = TestClient(create_validation_app(inertia_response))

    response = client.get("/search", headers={"X-Inertia": "true"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "page"]


def test_validation_error_locations_include_list_indexes() -> None:
    exc = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "items", 0, "name"),
                "msg": "Field required",
                "input": {},
            }
        ]
    )

    assert validation_errors_from_exception(exc) == {"items.0.name": "Field required"}


def test_validation_value_errors_use_original_exception_message() -> None:
    exc = RequestValidationError(
        [
            {
                "type": "value_error",
                "loc": ("body",),
                "msg": "Value error, Too late",
                "input": {},
                "ctx": {"error": ValueError("Too late")},
            }
        ]
    )

    assert validation_errors_from_exception(exc) == {"_form": "Too late"}


def test_validation_errors_keep_non_value_error_messages() -> None:
    exc = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "name"),
                "msg": "Field required",
                "input": {},
            },
            {
                "type": "int_parsing",
                "loc": ("body", "age"),
                "msg": "Input should be a valid integer",
                "input": "abc",
            },
        ]
    )

    assert validation_errors_from_exception(exc) == {
        "name": "Field required",
        "age": "Input should be a valid integer",
    }


def test_validation_errors_fall_back_for_non_string_messages() -> None:
    exc = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("body", "name"),
                "msg": None,
                "input": {},
            }
        ]
    )

    assert validation_errors_from_exception(exc) == {"name": "Invalid value"}


def test_pop_validation_errors_from_session_removes_stored_errors() -> None:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/users/create",
            "headers": [],
            "session": {
                "_cross_inertia_validation_errors": {
                    "errors": {"name": "Field required"},
                    "error_bag": "createUser",
                }
            },
        }
    )

    assert pop_validation_errors_from_session(request) == {
        "createUser": {"name": "Field required"}
    }
    assert "_cross_inertia_validation_errors" not in request.session
