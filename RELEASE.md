---
release type: patch
---

Add automatic FastAPI validation error handling for Inertia requests.

- Store FastAPI and Pydantic validation errors in the session and expose them once as `page.props.errors`
- Use `_form` for Pydantic model-level validation errors
- Document the FastAPI validation error flow
