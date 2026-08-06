---
release type: minor
---

Stabilize the Django adapter and align Cross-Inertia with Inertia.js v3.

- Add rescued deferred props and nested special-prop resolution.
- Preserve response status, flash, fragments, and protocol cache headers.
- Convert Django mutation redirects to `303 See Other` as required by Inertia.
- Improve async Django and typed FastAPI shared-data handling.
- Upgrade the bundled React clients and documentation to Inertia.js v3.
