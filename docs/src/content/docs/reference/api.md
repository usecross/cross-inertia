---
title: API Reference
description: Complete API reference for Cross-Inertia
---

This page documents all public APIs provided by Cross-Inertia.

## Inertia Class

The main class for rendering Inertia responses. Available as a dependency via `InertiaDep`.

### `inertia.render()`

Render an Inertia response with the specified component and props.

```python
def render(
    component: str,
    props: dict[str, Any] | None = None,
    errors: dict[str, str] | None = None,
    merge_props: list[str] | None = None,
    prepend_props: list[str] | None = None,
    deep_merge_props: list[str] | None = None,
    match_props_on: list[str] | None = None,
    scroll_props: dict[str, Any] | None = None,
    url: str | None = None,
    view_data: dict[str, Any] | None = None,
) -> JSONResponse | HTMLResponse | Response
```

**Parameters:**

- `component` (str): The name of the page component to render (e.g., `"Home"`, `"Users/Show"`)
- `props` (dict, optional): Props to pass to the component
- `errors` (dict, optional): Validation errors (triggers 422 status)
- `merge_props` (list, optional): Props to merge instead of replace (for infinite scroll)
- `prepend_props` (list, optional): Props to prepend instead of replace
- `deep_merge_props` (list, optional): Props to deep merge
- `match_props_on` (list, optional): Keys to match on when merging (e.g., `["id"]`)
- `scroll_props` (dict, optional): Configuration for infinite scroll prop merging
- `url` (str, optional): Override the URL for this response
- `view_data` (dict, optional): Extra data to pass to the template (not included in page props)

**Returns:** Response object (JSON for Inertia requests, HTML for initial visits)

**Example:**

```python
from inertia.fastapi import InertiaDep

@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    user = get_user(user_id)
    return inertia.render("Users/Show", {
        "user": user,
        "posts": get_user_posts(user_id)
    })
```

**With validation errors:**

```python
@app.post("/users")
async def create_user(inertia: InertiaDep):
    errors = validate_user(form_data)
    if errors:
        return inertia.render("Users/Create", {}, errors=errors)
    # ...
```

**With view data:**

```python
@app.get("/products/{id}")
async def product_page(id: int, inertia: InertiaDep):
    product = get_product(id)
    return inertia.render(
        "Product",
        {"product": product},
        view_data={
            "page_title": f"{product.name} - Our Store",
            "meta_description": product.description[:160],
        }
    )
```

### `inertia.location()`

Perform an external redirect (full page navigation).

```python
def location(url: str) -> Response
```

**Parameters:**

- `url` (str): The URL to redirect to (absolute or relative)

**Returns:** Response with 409 status and `X-Inertia-Location` header

**Example:**

```python
@app.get("/auth/github")
async def github_oauth(inertia: InertiaDep):
    oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    return inertia.location(oauth_url)
```

**Use cases:**
- OAuth providers
- Payment gateways
- External maps
- File downloads
- Non-Inertia pages

**Reference:** [External Redirects Guide](/guides/external-redirects/)

### `inertia.encrypt_history()`

Enable history encryption for the current page.

```python
def encrypt_history(encrypt: bool = True) -> Inertia
```

**Parameters:**

- `encrypt` (bool, optional): Whether to encrypt (default: `True`)

**Returns:** Self for method chaining

**Example:**

```python
@app.get("/account/transactions")
async def transactions(inertia: InertiaDep):
    inertia.encrypt_history()
    return inertia.render("Transactions", {
        "balance": user.balance,
        "transactions": user.get_transactions()
    })

# Method chaining
return inertia.encrypt_history().render("Transactions", {...})
```

**How it works:**
- Uses browser Web Crypto API (AES-GCM)
- Keys stored in sessionStorage
- Only works over HTTPS (except localhost)
- Protects sensitive data in browser history

**Reference:** [History Encryption Guide](/guides/history-encryption/)

### `inertia.clear_history()`

Clear encrypted history by rotating encryption keys.

```python
def clear_history(clear: bool = True) -> Inertia
```

**Parameters:**

- `clear` (bool, optional): Whether to clear (default: `True`)

**Returns:** Self for method chaining

**Example:**

```python
@app.post("/logout")
async def logout(inertia: InertiaDep):
    clear_user_session()
    inertia.clear_history()  # Rotate keys
    return inertia.render("Login", {})
```

**How it works:**
- Deletes current encryption key from sessionStorage
- Generates new key
- Makes previously encrypted pages unreadable
- Typically called on logout

**Reference:** [History Encryption Guide](/guides/history-encryption/)

### `inertia.back()`

Redirect back with errors (for form validation).

```python
def back(errors: dict[str, str] | None = None) -> JSONResponse | HTMLResponse | Response
```

**Parameters:**

- `errors` (dict, optional): Validation errors to display

**Returns:** Response object

**Example:**

```python
@app.post("/users")
async def create_user(inertia: InertiaDep):
    errors = validate_user(form_data)
    if errors:
        return inertia.back(errors=errors)
    # ...
```

**Note:** This is a convenience method. For more control, use `inertia.render()` directly.

## InertiaResponse Class

Core configuration class for Inertia responses.

### Constructor

```python
InertiaResponse(
    template_dir: str = "templates",
    vite_dev_url: str = "http://localhost:5173",
    manifest_path: str = "static/build/.vite/manifest.json",
    vite_entry: str | None = None,
    vite_config_path: str = "vite.config.ts",
)
```

**Parameters:**

- `template_dir` (str): Directory containing HTML template (default: `"templates"`)
- `vite_dev_url` (str): Vite dev server URL (default: `"http://localhost:5173"`)
- `manifest_path` (str): Path to Vite manifest.json (default: `"static/build/.vite/manifest.json"`)
- `vite_entry` (str, optional): Vite entry point (auto-detected if `None`)
- `vite_config_path` (str): Path to vite.config.ts for auto-detection (default: `"vite.config.ts"`)

**Example:**

```python
from inertia.fastapi import InertiaResponse

# Custom configuration
inertia_response = InertiaResponse(
    template_dir="my_templates",
    vite_dev_url="http://localhost:5174",
    manifest_path="dist/.vite/manifest.json",
    vite_entry="src/main.tsx"
)
```

**Reference:** [Configuration Guide](/guides/configuration/)

## InertiaMiddleware

Middleware for sharing data across all Inertia responses.

### Constructor

```python
InertiaMiddleware(
    app,
    share: Callable[[Request], dict] | None = None
)
```

**Parameters:**

- `app`: ASGI application
- `share` (callable, optional): Function that returns shared data

**Example:**

```python
from fastapi import FastAPI, Request
from inertia.fastapi import InertiaMiddleware

app = FastAPI()

def share_data(request: Request) -> dict:
    user = get_current_user(request)
    return {
        "auth": {"user": user},
        "flash": get_flash_message(request),
    }

app.add_middleware(InertiaMiddleware, share=share_data)
```

**Reference:** [Shared Data Guide](/guides/shared-data/)

## Type Aliases

### InertiaDep

FastAPI dependency for injecting Inertia instance.

```python
from inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {})
```

**Type:** `Annotated[Inertia, Depends(get_inertia)]`

## Utility Functions

### `read_vite_entry_from_config()`

Auto-detect Vite entry point from vite.config.ts/js.

```python
def read_vite_entry_from_config(
    vite_config_path: str = "vite.config.ts"
) -> str | None
```

**Parameters:**

- `vite_config_path` (str): Path to vite config file

**Returns:** Entry point path or `None` if not found

**Example:**

```python
from inertia.fastapi import read_vite_entry_from_config

entry = read_vite_entry_from_config("vite.config.ts")
print(entry)  # "frontend/app.tsx"
```

## Template Functions

### `vite()`

Include Vite assets in your HTML template.

**Signature:**

```jinja2
{{ vite(entry: str | None = None)|safe }}
```

**Parameters:**

- `entry` (str, optional): Custom entry point (uses default if not specified)

**Returns:** HTML string with script/link tags

**Example:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- Default entry point -->
    {{ vite()|safe }}
    
    <!-- Custom entry point -->
    {{ vite('admin/app.js')|safe }}
</head>
<body>
    <div id="app" data-page='{{ page }}'></div>
</body>
</html>
```

**Development mode output:**

```html
<script type="module" src="http://localhost:5173/@vite/client"></script>
<script type="module" src="http://localhost:5173/frontend/app.tsx"></script>
```

**Production mode output:**

```html
<link rel="stylesheet" href="/static/build/assets/app-abc123.css">
<script type="module" src="/static/build/assets/app-xyz789.js"></script>
```

### `page` Variable

The current page data as JSON string.

**Type:** `str` (JSON-encoded page data)

**Example:**

```html
<div id="app" data-page='{{ page }}'></div>
```

**Note:** Always use single quotes around `{{ page }}` to avoid escaping issues.

## HTTP Headers

### Request Headers

**`X-Inertia`**
- Value: `"true"`
- Indicates this is an Inertia request

**`X-Inertia-Version`**
- Value: Asset version string
- Used for asset version mismatch detection

**`X-Inertia-Partial-Data`**
- Value: Comma-separated list of props
- Requests only specific props (partial reload)

**`X-Inertia-Partial-Component`**
- Value: Component name
- Specifies which component is making the partial request

### Response Headers

**`X-Inertia`**
- Value: `"true"`
- Confirms this is an Inertia response

**`X-Inertia-Location`** (409 responses only)
- Value: URL string
- Triggers external redirect

**`Vary`**
- Value: `"X-Inertia"`
- Ensures proper caching

## Status Codes

**200 OK**
- Successful Inertia response

**303 See Other**
- Internal redirect (use with `RedirectResponse`)

**409 Conflict**
- External redirect or asset version mismatch
- Includes `X-Inertia-Location` header

**422 Unprocessable Entity**
- Validation errors
- Automatically set when `errors` param is provided

## Type Hints

For TypeScript users, here are common type definitions:

```typescript
// Page props interface
interface PageProps {
  [key: string]: any
}

// Shared props interface
interface SharedProps {
  auth: {
    user: User | null
  }
  flash?: {
    message: string
    category: 'success' | 'error' | 'warning' | 'info'
  }
}

// Inertia page type
import { Page } from '@inertiajs/core'

type InertiaPage<P = PageProps> = Page<P & SharedProps>
```

## Next Steps

- [Quick Start](/getting-started/quick-start/) - Build your first app
- [Configuration](/guides/configuration/) - Customize your setup
- [Guides](/guides/) - Learn about features in depth
