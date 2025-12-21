---
release type: minor
---

Add Django framework support

- Add `inertia.django` module with full Inertia.js protocol support
- Implement `render()`, `location()`, `@inertia` decorator, and `InertiaViewMixin` for Django views
- Add `InertiaMiddleware` for shared data injection
- Add `{% inertia_head %}` and `{% inertia_body %}` template tags
- Automatic Vite dev server startup when using `runserver`
- DRF-style settings pattern via `settings.CROSS_INERTIA` dict
- Support all prop types: `optional()`, `always()`, `defer()`
- Refactor core modules to avoid FastAPI imports when using Django
- Add shared `SyncViteProcess` and `AsyncViteProcess` classes for Vite dev server management
