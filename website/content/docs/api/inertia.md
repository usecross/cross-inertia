---
title: Inertia Class
description: API reference for the Inertia class.
order: 12
section: API Reference
---

## InertiaDep

The `InertiaDep` type is a FastAPI dependency that provides access to the Inertia instance.

```python
from cross_inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {"message": "Hello"})
```

## FastAPI validation handlers

Use `inertia_exception_handlers()` when creating your FastAPI app to store FastAPI/Pydantic validation errors from mutating Inertia requests in the session, redirect back, and expose those errors once as `props.errors`.

```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from cross_inertia.fastapi import inertia_exception_handlers

app = FastAPI(exception_handlers=inertia_exception_handlers())
app.add_middleware(SessionMiddleware, secret_key="change-me")
```

If you need to compose handlers yourself, register `inertia_validation_exception_handler` for FastAPI's `RequestValidationError`.

## Methods

### render()

Render an Inertia page component.

```python
inertia.render(
    component: str,
    props: dict = {},
    view_data: dict = {},
    encrypt_history: bool = False,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `component` | `str` | The name of the page component to render |
| `props` | `dict` | Props to pass to the component |
| `view_data` | `dict` | Additional data for the template (not passed to component) |
| `encrypt_history` | `bool` | Whether to encrypt this page in browser history |

**Returns:** `InertiaResponse`

### location()

Perform an external redirect (non-Inertia URL).

```python
inertia.location(url: str)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | The URL to redirect to |

**Returns:** `Response`

**Example:**

```python
@app.get("/oauth")
async def oauth_redirect(inertia: InertiaDep):
    return inertia.location("https://github.com/login/oauth")
```
