"""Inertia protocol behavior provided by the Django middleware."""

import asyncio

import pytest
from asgiref.sync import iscoroutinefunction
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect

from cross_inertia.django.middleware import InertiaMiddleware


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_inertia_mutation_redirects_are_converted_to_303(rf, method):
    request = getattr(rf, method)("/resource/", HTTP_X_INERTIA="true")
    middleware = InertiaMiddleware(
        lambda request: HttpResponseRedirect("/resource/complete/")
    )

    response = middleware(request)

    assert response.status_code == 303
    assert response["Location"] == "/resource/complete/"


@pytest.mark.parametrize(
    ("method", "is_inertia"),
    [
        ("get", True),
        ("post", True),
        ("patch", False),
    ],
)
def test_other_redirects_remain_302(rf, method, is_inertia):
    headers = {"HTTP_X_INERTIA": "true"} if is_inertia else {}
    request = getattr(rf, method)("/resource/", **headers)
    middleware = InertiaMiddleware(
        lambda request: HttpResponseRedirect("/resource/complete/")
    )

    response = middleware(request)

    assert response.status_code == 302


def test_async_inertia_mutation_redirect_is_converted_to_303(rf):
    async def get_response(request):
        return HttpResponseRedirect("/resource/complete/")

    request = rf.patch("/resource/", HTTP_X_INERTIA="true")
    middleware = InertiaMiddleware(get_response)

    response = asyncio.run(middleware(request))

    assert response.status_code == 303


def test_async_middleware_is_marked_as_coroutine_function():
    async def get_response(request):
        return HttpResponse()

    middleware = InertiaMiddleware(get_response)

    assert iscoroutinefunction(middleware)


@pytest.mark.django_db
def test_async_middleware_runs_sync_share_outside_async_context(rf):
    def share_data(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_value = cursor.fetchone()[0]
        return {"database": database_value}

    async def get_response(request):
        return HttpResponse()

    request = rf.get("/resource/")
    middleware = InertiaMiddleware(get_response)
    middleware._share_func = share_data
    middleware._share_func_loaded = True

    response = asyncio.run(middleware(request))

    assert response.status_code == 200
    assert request._inertia_shared == {"database": 1}
