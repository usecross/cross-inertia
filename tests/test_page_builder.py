"""Unit tests for the shared Inertia page builder."""

from __future__ import annotations

from typing import Any

from cross_web import TestingRequestAdapter

from cross_inertia import defer, once, optional
from cross_inertia._page import (
    PageBuildResult,
    PageRenderOptions,
    PageRequestContext,
    build_page_request_context,
    build_inertia_page,
)


def build_result(
    props: dict[str, Any],
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    shared_data: dict[str, Any] | None = None,
    partial_component: str | None = None,
    partial_only: list[str] | None = None,
    partial_except: list[str] | None = None,
    reset_props: list[str] | None = None,
    except_once_props: set[str] | None = None,
    errors: dict[str, str] | None = None,
) -> PageBuildResult:
    request_headers = headers or {}
    is_inertia = request_headers.get("X-Inertia") == "true"

    return build_inertia_page(
        PageRequestContext(
            method=method,
            headers=request_headers,
            current_url="http://testserver/test",
            page_url="/test",
            shared_data=shared_data or {},
            asset_version="dev",
            is_inertia=is_inertia,
            is_prefetch=request_headers.get("Purpose") == "prefetch",
            partial_component=partial_component,
            partial_only=partial_only or [],
            partial_except=partial_except or [],
            reset_props=reset_props or [],
            except_once_props=except_once_props or set(),
            error_bag=request_headers.get("X-Inertia-Error-Bag"),
            version_conflict_location="http://testserver/test",
        ),
        PageRenderOptions(
            component="TestComponent",
            props=props,
            errors=errors,
            merge_props=["users", "users.data"] if reset_props else None,
        ),
    )


def test_partial_except_takes_precedence_when_both_headers_are_present() -> None:
    result = build_result(
        {
            "profile": {
                "name": "John",
                "email": "john@example.com",
            },
            "stats": {"count": 42},
        },
        headers={"X-Inertia": "true"},
        partial_component="TestComponent",
        partial_only=["profile", "stats"],
        partial_except=["profile.email"],
    )

    assert result.page_data is not None
    assert result.page_data["props"] == {
        "profile": {"name": "John"},
        "stats": {"count": 42},
    }


def test_build_page_request_context_normalizes_url_and_inertia_headers() -> None:
    context = build_page_request_context(
        adapter=TestingRequestAdapter(
            method="GET",
            headers={
                "X-Inertia": "true",
                "Purpose": "prefetch",
                "X-Inertia-Partial-Component": "TestComponent",
                "X-Inertia-Partial-Data": "plans, profile.name",
                "X-Inertia-Partial-Except": "stats",
                "X-Inertia-Reset": "filters",
                "X-Inertia-Except-Once-Props": "plans-cache",
                "X-Inertia-Error-Bag": "profile",
            },
            url="http://testserver/billing?page=2",
        ),
        shared_data={"auth": {"user": "patrick"}},
        asset_version="dev",
    )

    assert context.current_url == "http://testserver/billing?page=2"
    assert context.page_url == "/billing?page=2"
    assert context.shared_data == {"auth": {"user": "patrick"}}
    assert context.is_inertia is True
    assert context.is_prefetch is True
    assert context.partial_component == "TestComponent"
    assert context.partial_only == ["plans", "profile.name"]
    assert context.partial_except == ["stats"]
    assert context.reset_props == ["filters"]
    assert context.except_once_props == {"plans-cache"}
    assert context.error_bag == "profile"
    assert context.version_conflict_location == "http://testserver/billing?page=2"


def test_nested_optional_props_are_excluded_until_explicitly_requested() -> None:
    initial = build_result(
        {
            "profile": {
                "name": "John",
                "permissions": optional(lambda: ["invite"]),
            },
        },
        headers={"X-Inertia": "true"},
    )

    assert initial.page_data is not None
    assert initial.page_data["props"] == {"profile": {"name": "John"}}

    partial = build_result(
        {
            "profile": {
                "name": "John",
                "permissions": optional(lambda: ["invite"]),
            },
        },
        headers={"X-Inertia": "true"},
        partial_component="TestComponent",
        partial_only=["profile.permissions"],
    )

    assert partial.page_data is not None
    assert partial.page_data["props"] == {"profile": {"permissions": ["invite"]}}


def test_once_props_emit_metadata_and_skip_remembered_values() -> None:
    result = build_result(
        {
            "plans": once(lambda: ["starter", "pro"], key="plans-cache", until=60),
        },
        headers={"X-Inertia": "true"},
        except_once_props={"plans-cache"},
    )

    assert result.page_data is not None
    assert "plans" not in result.page_data["props"]
    assert result.page_data["onceProps"]["plans-cache"]["prop"] == "plans"
    assert isinstance(result.page_data["onceProps"]["plans-cache"]["expiresAt"], int)


def test_partial_requests_refresh_once_props_even_when_client_remembered_them() -> None:
    result = build_result(
        {
            "plans": once(lambda: ["starter", "pro"], key="plans-cache", until=60),
        },
        headers={"X-Inertia": "true"},
        partial_component="TestComponent",
        partial_only=["plans"],
        except_once_props={"plans-cache"},
    )

    assert result.page_data is not None
    assert result.page_data["props"]["plans"] == ["starter", "pro"]
    assert result.page_data["onceProps"]["plans-cache"]["prop"] == "plans"


def test_once_wrapped_deferred_props_are_removed_from_deferred_metadata_when_remembered() -> (
    None
):
    result = build_result(
        {
            "permissions": once(
                defer(lambda: ["invite"], group="sidebar"),
                key="permissions-cache",
            ),
        },
        headers={"X-Inertia": "true"},
        except_once_props={"permissions-cache"},
    )

    assert result.page_data is not None
    assert result.page_data["props"] == {}
    assert "deferredProps" not in result.page_data
    assert result.page_data["onceProps"]["permissions-cache"]["prop"] == "permissions"


def test_shared_data_merges_before_page_props() -> None:
    result = build_result(
        {
            "auth": {"user": "page-user"},
            "message": "Hello",
        },
        headers={"X-Inertia": "true"},
        shared_data={
            "auth": {"user": "shared-user"},
            "flash": {"msg": "saved"},
        },
    )

    assert result.page_data is not None
    assert result.page_data["props"]["auth"] == {"user": "page-user"}
    assert result.page_data["props"]["flash"] == {"msg": "saved"}


def test_version_conflict_only_applies_to_get_inertia_requests() -> None:
    get_result = build_result(
        {"message": "Hello"},
        method="GET",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Version": "stale-version",
        },
    )

    assert get_result.version_conflict_location == "http://testserver/test"

    post_result = build_result(
        {"message": "Hello"},
        method="POST",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Version": "stale-version",
        },
    )

    assert post_result.version_conflict_location is None
    assert post_result.page_data is not None


def test_reset_props_filter_nested_merge_metadata() -> None:
    result = build_result(
        {"users": [{"id": 1}]},
        headers={"X-Inertia": "true"},
        reset_props=["users"],
    )

    assert result.page_data is not None
    assert result.page_data["resetProps"] == ["users"]
    assert "mergeProps" not in result.page_data
