# Cross-Inertia Examples

Example applications demonstrating cross-inertia with different Python web frameworks.

## FastAPI + React Example

See [fastapi/README.md](./fastapi/README.md) for the complete FastAPI + React cat adoption demo (PurrfectHome).

### Quick Start

```bash
# Terminal 1: Start Vite dev server
cd examples/fastapi
bun install
bun run dev

# Terminal 2: Start FastAPI server
cd examples/fastapi
uv run uvicorn main:app --reload
```

Then visit http://localhost:8000

## Features Demonstrated

- ✅ Page rendering with props
- ✅ Form submissions with validation
- ✅ Partial reloads
- ✅ Shared data (flash messages, auth)
- ✅ External redirects
- ✅ History encryption
- ✅ Asset versioning
- ✅ Vite integration (dev + production)

## Adding More Frameworks

Want to add Django, Flask, or another framework? Follow the structure:

```
examples/
├── fastapi/          # FastAPI implementation
│   ├── main.py
│   ├── frontend/     # React components
│   └── templates/
└── django/           # Future: Django implementation
    ├── views.py
    └── ...
```

Each framework example should demonstrate the same core features.
