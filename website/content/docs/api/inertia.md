---
title: Inertia Class
description: API reference for the Inertia class.
order: 12
section: API Reference
---

## InertiaDep

The `InertiaDep` type is a FastAPI dependency that provides access to the Inertia instance.

```python
from inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {"message": "Hello"})
```

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

### back()

Return to the previous page with optional errors.

```python
inertia.back(errors: dict = {})
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `errors` | `dict` | Validation errors to pass back |

**Returns:** `Response`

**Example:**

```python
@app.post("/users")
async def create_user(request: Request, inertia: InertiaDep):
    form = await request.form()
    if not form.get("email"):
        return inertia.back(errors={"email": "Email is required"})
    # ... create user
```

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
