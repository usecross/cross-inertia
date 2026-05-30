from __future__ import annotations

from enum import Enum

import pytest
from pydantic import BaseModel, Field

from cross_inertia._exceptions import InertiaSchemaError
from cross_inertia._schema import validate_props_with_schema


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class UserRecord(BaseModel):
    id: int
    name: str
    password_hash: str


class UserPublic(BaseModel):
    id: int
    name: str


class PostPublic(BaseModel):
    id: int
    title: str
    status: PostStatus


class CountsByStatus(BaseModel):
    draft: int
    published: int


class PostsIndexProps(BaseModel):
    user: UserPublic
    posts: list[PostPublic]
    counts: CountsByStatus


class ConstrainedProps(BaseModel):
    count: int = Field(ge=1)


def test_schema_serializes_pydantic_and_attribute_objects_to_json_values() -> None:
    result = validate_props_with_schema(
        {
            "user": UserRecord(id=1, name="Ada", password_hash="secret"),
            "posts": [
                {"id": 10, "title": "Draft", "status": PostStatus.DRAFT},
                PostPublic(id=11, title="Published", status=PostStatus.PUBLISHED),
            ],
            "counts": CountsByStatus(draft=1, published=1),
        },
        schema=PostsIndexProps,
        require_required_fields=True,
        allowed_missing_fields=set(),
    )

    assert result == {
        "user": {"id": 1, "name": "Ada"},
        "posts": [
            {"id": 10, "title": "Draft", "status": "draft"},
            {"id": 11, "title": "Published", "status": "published"},
        ],
        "counts": {"draft": 1, "published": 1},
    }


def test_schema_leaves_unknown_props_unchanged() -> None:
    result = validate_props_with_schema(
        {
            "posts": [{"id": 10, "title": "Draft", "status": "draft"}],
            "shared": {"csrf": "abc"},
        },
        schema=PostsIndexProps,
        require_required_fields=False,
        allowed_missing_fields=set(),
    )

    assert result == {
        "posts": [{"id": 10, "title": "Draft", "status": "draft"}],
        "shared": {"csrf": "abc"},
    }


def test_schema_raises_for_missing_required_field_on_full_response() -> None:
    with pytest.raises(InertiaSchemaError) as exc_info:
        validate_props_with_schema(
            {
                "user": UserRecord(id=1, name="Ada", password_hash="secret"),
                "posts": [{"id": 10, "title": "Draft", "status": "draft"}],
            },
            schema=PostsIndexProps,
            require_required_fields=True,
            allowed_missing_fields=set(),
        )

    message = str(exc_info.value)
    assert "counts" in message


def test_schema_allows_intentionally_omitted_required_field() -> None:
    result = validate_props_with_schema(
        {
            "posts": [{"id": 10, "title": "Draft", "status": "draft"}],
        },
        schema=PostsIndexProps,
        require_required_fields=True,
        allowed_missing_fields={"user", "counts"},
    )

    assert result == {
        "posts": [{"id": 10, "title": "Draft", "status": "draft"}],
    }


def test_schema_validation_error_includes_prop_name() -> None:
    with pytest.raises(InertiaSchemaError) as exc_info:
        validate_props_with_schema(
            {
                "posts": [{"id": "bad", "title": "Draft", "status": "draft"}],
            },
            schema=PostsIndexProps,
            require_required_fields=False,
            allowed_missing_fields=set(),
        )

    message = str(exc_info.value)
    assert "posts" in message


def test_schema_preserves_field_constraints() -> None:
    with pytest.raises(InertiaSchemaError) as exc_info:
        validate_props_with_schema(
            {"count": 0},
            schema=ConstrainedProps,
            require_required_fields=True,
            allowed_missing_fields=set(),
        )

    assert "count" in str(exc_info.value)
