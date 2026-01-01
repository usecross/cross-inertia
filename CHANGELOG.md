

0.12.0 - 2026-01-01
-------------------

Add Django framework support

- Add `inertia.django` module with full Inertia.js protocol support
- Implement `render()`, `location()`, `@inertia` decorator, and `InertiaViewMixin` for Django views
- Add `InertiaMiddleware` for shared data injection
- DRF-style settings pattern via `settings.CROSS_INERTIA` dict
- Support all prop types: `optional()`, `always()`, `defer()`
- Automatic Vite dev server startup when using `runserver`

Aligned template API between frameworks:

- Add `inertia_head()` and `inertia_body()` Jinja2 functions for FastAPI
- Add `{% inertia_head %}` and `{% inertia_body %}` Django template tags
- Both output Vite tags, SSR content, and app container consistently

Internal improvements:

- Add shared `SyncViteProcess` and `AsyncViteProcess` classes for Vite dev server management
- Refactor core modules to avoid FastAPI imports when using Django
