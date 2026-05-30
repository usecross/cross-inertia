---
release type: minor
---

Add optional Pydantic schema support for Inertia page props.

- Add a `schema=` argument to render APIs so page props can be validated and
  serialized through Pydantic models
- Support schema validation during partial reloads, deferred props, optional
  props, and remembered `once()` props
- Expose `InertiaSchemaError` for schema validation failures
- Document prop schemas, including using public models to reduce exposed fields
- Add tests for schema serialization, validation, partial reload behavior, and
  framework integration
