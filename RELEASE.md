---
release type: minor
---

Add shared v3 page building, once props, and script-element bootstrap support

- add the shared internal page builder used by both FastAPI and Django
- add public `once()` props with shared-data support, expiration, and refresh handling
- switch initial HTML page bootstrapping to Inertia's script-element format
- update examples, docs, tests, and nox sessions for the new bootstrap flow
