---
release type: minor
---

Add Django framework support

- Add `inertia.django` module with full Inertia.js protocol support
- Implement `render()`, `location()`, `@inertia` decorator, and `InertiaViewMixin` for Django views
- Add `InertiaMiddleware` for shared data injection via `INERTIA_SHARE` setting
- Add `{% vite %}` template tag for Vite asset injection in Django templates
- Automatic Vite dev server startup when using `runserver`
- Support all prop types: `optional()`, `always()`, `defer()`
- Refactor core modules to avoid FastAPI imports when using Django
