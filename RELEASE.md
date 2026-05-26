---
release type: minor
---

This release adds FastAPI validation error handling for Inertia form submissions.

- Add declarative FastAPI exception handlers for validation failures
- Store validation errors in the session and expose them once as `props.errors`
- Redirect validation failures back using the same-origin referrer or stored previous Inertia URL
- Preserve error bags for scoped form errors
- Update validation documentation to match the Inertia protocol
