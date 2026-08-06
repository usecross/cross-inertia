# Cross-Inertia Roadmap

Cross-Inertia is an Inertia.js v3 server adapter for Python web frameworks.
For individual work items, see [GitHub Issues](https://github.com/usecross/cross-inertia/issues).

## Framework support

- **FastAPI / Starlette** — supported and covered by unit and browser tests.
- **Django 4.2+** — supported and covered by unit tests.
- **Other ASGI frameworks** — can use the framework-neutral core and `cross-web`
  adapters; dedicated integrations are considered as demand emerges.

## Current capabilities

- Inertia request and response protocol, including asset version conflicts.
- Shared, optional, deferred, once, merge, and rescued props.
- Error bags, flash data, history encryption, and fragment preservation.
- Internal and external redirects.
- Vite development, production manifests, and React Fast Refresh.
- Client-side rendering and optional server-side rendering.
- FastAPI dependency helpers and Django middleware, shortcuts, and template tags.

## Stabilization priorities

1. Keep protocol behavior aligned with the current Inertia.js v3 client.
2. Expand Django end-to-end coverage alongside the existing FastAPI example.
3. Document production deployment patterns for assets and SSR processes.
4. Maintain the supported Python 3.10–3.14 test matrix and framework type coverage.
5. Reach a stable 1.0 API after production feedback from both framework adapters.

## Design principles

- Follow the upstream Inertia protocol instead of inventing framework-specific behavior.
- Keep framework integrations thin and build shared behavior in the core package.
- Prefer explicit, typed configuration and conventional framework APIs.
- Preserve backwards compatibility within the 0.x line where practical, while
  correcting protocol violations promptly.

## Contributing

Run the relevant checks before opening a pull request:

```bash
nox -s lint
nox -s typecheck
nox -s tests-3.14
```

See [AGENTS.md](./AGENTS.md) and the repository issues for current conventions
and scoped tasks.
