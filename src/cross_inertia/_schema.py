from __future__ import annotations

from operator import getitem
from typing import Annotated, Any

from ._exceptions import InertiaSchemaError


def validate_props_with_schema(
    props: dict[str, Any],
    *,
    schema: Any,
    require_required_fields: bool,
    allowed_missing_fields: set[str],
) -> dict[str, Any]:
    """Validate and serialize included top-level props against a Pydantic model."""
    TypeAdapter, Field, validation_exceptions = _get_pydantic_tools()
    model_fields = _get_model_fields(schema)
    schema_name = _get_schema_name(schema)

    if require_required_fields:
        missing_fields = [
            name
            for name, field in model_fields.items()
            if name not in props
            and name not in allowed_missing_fields
            and _field_is_required(field)
        ]
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise InertiaSchemaError(
                f"Inertia props are missing required schema field(s): {missing}"
            )

    serialized: dict[str, Any] = {}
    for name, value in props.items():
        field = model_fields.get(name)
        if field is None:
            serialized[name] = value
            continue

        adapter = _make_type_adapter(field, TypeAdapter, Field)
        try:
            validated = adapter.validate_python(value, from_attributes=True)
            serialized[name] = adapter.dump_python(
                validated,
                mode="json",
                by_alias=True,
            )
        except validation_exceptions as exc:
            raise InertiaSchemaError(
                f"Inertia prop '{name}' does not match schema {schema_name}"
            ) from exc

    return serialized


def _get_pydantic_tools() -> tuple[Any, Any, tuple[type[Exception], ...]]:
    try:
        from pydantic import Field, TypeAdapter, ValidationError
        from pydantic_core import PydanticSerializationError
    except ImportError as exc:
        raise InertiaSchemaError(
            "render(..., schema=...) requires pydantic>=2 to be installed"
        ) from exc

    return TypeAdapter, Field, (ValidationError, PydanticSerializationError, TypeError)


def _make_type_adapter(field: Any, TypeAdapter: Any, Field: Any) -> Any:
    field_dict = _field_asdict(field)
    annotated_args = (
        field_dict["annotation"],
        *field_dict["metadata"],
        Field(**field_dict["attributes"]),
    )
    # Keeps Annotated tuple unpacking explicit while remaining valid on Python 3.10.
    return TypeAdapter(getitem(Annotated, annotated_args))


def _field_asdict(field: Any) -> dict[str, Any]:
    asdict = getattr(field, "asdict", None)
    if callable(asdict):
        return asdict()

    attributes = {}
    for attr in (
        "default",
        "default_factory",
        "alias",
        "alias_priority",
        "validation_alias",
        "serialization_alias",
        "title",
        "field_title_generator",
        "description",
        "examples",
        "exclude",
        "exclude_if",
        "discriminator",
        "deprecated",
        "json_schema_extra",
        "frozen",
        "validate_default",
        "repr",
        "init",
        "init_var",
        "kw_only",
    ):
        value = getattr(field, attr, None)
        if value is not None:
            attributes[attr] = value

    return {
        "annotation": field.annotation,
        "metadata": getattr(field, "metadata", []),
        "attributes": attributes,
    }


def _get_model_fields(schema: Any) -> dict[str, Any]:
    schema_type = schema if isinstance(schema, type) else type(schema)
    model_fields = getattr(schema_type, "model_fields", None)
    if model_fields is None:
        raise InertiaSchemaError(
            "render(..., schema=...) expects a Pydantic v2 model class"
        )

    return dict(model_fields)


def _get_schema_name(schema: Any) -> str:
    return str(getattr(schema, "__name__", type(schema).__name__))


def _field_is_required(field: Any) -> bool:
    is_required = getattr(field, "is_required", None)
    if callable(is_required):
        return bool(is_required())
    return bool(is_required)
