from __future__ import annotations

from typing import TypeAlias, cast
from urllib.parse import urlparse

from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from starlette.responses import Response

from cross_inertia._types import ValidationErrors

_DEFAULT_SESSION_KEY = "_cross_inertia_validation_errors"
_PREVIOUS_URL_SESSION_KEY = "_cross_inertia_previous_url"
_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_LOCATION_PREFIXES = {"body", "form"}

ErrorLocation: TypeAlias = tuple[str | int, ...]


def inertia_exception_handlers() -> dict:
    """Return FastAPI exception handlers for Inertia integrations."""

    return {RequestValidationError: inertia_validation_exception_handler}


async def inertia_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> Response:
    """FastAPI exception handler for Inertia validation failures."""

    if not _should_flash_validation_errors(request):
        return await request_validation_exception_handler(request, exc)

    if "session" not in request.scope:
        raise RuntimeError(
            "Automatic Inertia validation errors require SessionMiddleware. "
            "Add starlette.middleware.sessions.SessionMiddleware before "
            "registering inertia_validation_exception_handler."
        )

    request.session[_DEFAULT_SESSION_KEY] = {
        "errors": validation_errors_from_exception(exc),
        "error_bag": request.headers.get("X-Inertia-Error-Bag"),
    }

    return RedirectResponse(_redirect_back_url(request), status_code=303)


def pop_validation_errors_from_session(request: Request) -> ValidationErrors | None:
    try:
        payload = request.session.pop(_DEFAULT_SESSION_KEY)
    except (AssertionError, KeyError):
        return None

    if not isinstance(payload, dict):
        return None

    errors = payload.get("errors")
    if not isinstance(errors, dict) or not errors:
        return None
    validation_errors = cast(ValidationErrors, errors)

    error_bag = payload.get("error_bag")
    if isinstance(error_bag, str) and error_bag:
        return {error_bag: validation_errors}

    return validation_errors


def store_current_url_as_previous_url(request: Request) -> None:
    if request.method.upper() != "GET":
        return

    try:
        request.session[_PREVIOUS_URL_SESSION_KEY] = _current_path_and_query(request)
    except AssertionError:
        return


def validation_errors_from_exception(exc: RequestValidationError) -> ValidationErrors:
    errors: ValidationErrors = {}

    for error in exc.errors():
        location = cast(ErrorLocation, error.get("loc", ()))
        field = _error_location_to_field_path(location)
        if field in errors:
            continue

        message = error.get("msg")
        errors[field] = message if isinstance(message, str) else "Invalid value"

    return errors


def _should_flash_validation_errors(request: Request) -> bool:
    return (
        request.headers.get("X-Inertia") == "true"
        and request.method.upper() in _MUTATING_METHODS
    )


def _error_location_to_field_path(location: ErrorLocation) -> str:
    parts = [str(part) for part in location]
    if parts and parts[0] in _LOCATION_PREFIXES:
        parts = parts[1:]

    if not parts or parts == ["__root__"]:
        return "form"

    return ".".join(parts)


def _redirect_back_url(request: Request) -> str:
    referer = request.headers.get("Referer")

    if referer:
        parsed_referer = urlparse(referer)

        if not parsed_referer.scheme and not parsed_referer.netloc:
            return referer

        if (
            parsed_referer.scheme == request.url.scheme
            and parsed_referer.netloc == request.url.netloc
        ):
            path = parsed_referer.path or "/"

            if parsed_referer.query:
                path = f"{path}?{parsed_referer.query}"

            if parsed_referer.fragment:
                path = f"{path}#{parsed_referer.fragment}"

            return path

    try:
        previous_url = request.session[_PREVIOUS_URL_SESSION_KEY]
    except (AssertionError, KeyError):
        previous_url = None

    if isinstance(previous_url, str) and previous_url.startswith("/"):
        return previous_url

    return "/"


def _current_path_and_query(request: Request) -> str:
    path = request.url.path or "/"

    if request.url.query:
        path = f"{path}?{request.url.query}"

    return path
