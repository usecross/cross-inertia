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
    schema: type[BaseModel] | None = None,
    view_data: dict = {},
    encrypt_history: bool = False,
    status_code: int = 200,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `component` | `str` | The name of the page component to render |
| `props` | `dict` | Props to pass to the component |
| `schema` | `type[BaseModel] \| None` | Optional Pydantic model used to validate and serialize included page props |
| `view_data` | `dict` | Additional data for the template (not passed to component) |
| `encrypt_history` | `bool` | Whether to encrypt this page in browser history |
| `status_code` | `int` | HTTP status for both Inertia JSON and initial HTML responses |

Use a non-200 status when an error page itself should retain the underlying
HTTP semantics:

```python
return inertia.render("ErrorPage", {"status": 403}, status_code=403)
```

### Prop schemas

Use `schema=` to validate and serialize page props without manually calling
`model_dump(mode="json")` in every route. Schemas also let you reduce the
fields exposed for a prop: pass your application object, then declare the
public response shape with a Pydantic model.

```python
from pydantic import BaseModel


class UserPublic(BaseModel):
    id: int
    name: str


class PostPublic(BaseModel):
    id: int
    title: str


class CountsByStatus(BaseModel):
    draft: int
    published: int


class PostsIndexProps(BaseModel):
    user: UserPublic
    posts: list[PostPublic]
    counts: CountsByStatus


@app.get("/posts")
async def posts(inertia: InertiaDep):
    return inertia.render(
        "Posts/Index",
        {
            "user": current_user,
            "posts": posts,
            "counts": lambda: count_posts_by_status(session),
        },
        schema=PostsIndexProps,
    )
```

In this example, `current_user` can contain additional fields such as
`username` or `password_hash`. Because the page schema declares
`user: UserPublic`, only the fields on `UserPublic` are serialized into the
Inertia response.

The schema describes the full page prop contract. During partial reloads,
deferred props, optional props, and remembered `once()` props, Cross-Inertia
validates only the props included in the current response. A required field
such as `counts: CountsByStatus` may be omitted from a partial response when
the client requests only another prop, but it must match `CountsByStatus`
whenever it is sent.

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
