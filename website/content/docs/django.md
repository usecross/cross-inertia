---
title: Django
description: Use Cross-Inertia with Django.
order: 3
section: Getting Started
---

Cross-Inertia provides full Django support with a familiar API that follows Django conventions.

## Installation

Install Cross-Inertia:

```bash
pip install "cross-inertia[django]"
```

## Configuration

Add `cross_inertia.django` to your installed apps and middleware:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'cross_inertia.django',
]

MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cross_inertia.django.InertiaMiddleware',
]
```

Configure Inertia using the `CROSS_INERTIA` settings dict (similar to Django REST Framework):

```python
# settings.py

CROSS_INERTIA = {
    'LAYOUT': 'base.html',              # Template for initial page loads
    'VITE_ENTRY': 'frontend/app.tsx',   # Vite entry point
    'VITE_PORT': 'auto',                # Free port picked at startup, or a number
    'VITE_BASE': '/',                   # Must match `base` in vite.config
    'VITE_REACT_REFRESH': True,         # Set False for Vue/Svelte entries
    'MANIFEST_PATH': 'static/build/.vite/manifest.json',
    'SSR_ENABLED': False,               # Enable for server-side rendering
    'SHARE': 'myapp.inertia.share_data',  # Dotted path to share function
}
```

All settings are optional. Settings backed by `InertiaConfig` share its
defaults, so Django and FastAPI behave the same out of the box (Vite entry
`frontend/app.tsx`, a free port, `bun run dev`). `ASSET_URL_PREFIX` is derived
from Django's `STATIC_URL` unless explicitly configured.

## Creating Views

### Using `render()`

The simplest way to render Inertia pages:

```python
# views.py
from cross_inertia.django import render

def home(request):
    return render(request, 'Home', {
        'message': 'Hello World',
        'user': request.user.username,
    })
```

### Using the `@inertia` decorator

For cleaner views that just return props:

```python
from cross_inertia.django import inertia

@inertia('Home')
def home(request):
    return {
        'message': 'Hello World',
        'user': request.user.username,
    }
```

### Using Class-Based Views

Mix in `InertiaViewMixin` with your class-based views:

```python
from django.views import View
from cross_inertia.django import InertiaViewMixin

class HomeView(InertiaViewMixin, View):
    component = 'Home'

    def get_props(self, request):
        return {
            'message': 'Hello World',
            'method': request.method,
        }
```

## Template Setup

Create your base template with Inertia template tags:

```html
{% load inertia %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    {% inertia_head %}
</head>
<body>
    {% inertia_body %}
</body>
</html>
```

The template tags:
- `{% inertia_head %}` - Outputs Vite script/style tags and SSR head content
- `{% inertia_body %}` - Outputs the initial page JSON script and app container

## Prop Types

Use prop wrappers from the main `inertia` package (they're framework-agnostic):

```python
from cross_inertia import optional, always, defer
from cross_inertia.django import render

def dashboard(request):
    return render(request, 'Dashboard', {
        'user': get_user(request),                    # Regular prop
        'permissions': optional(get_permissions),     # Only when requested
        'navigation': always(get_navigation),         # Always included
        'analytics': defer(get_analytics),            # Loaded after render
    })
```

## Shared Data

Create a function that returns shared data for all pages:

```python
# myapp/inertia.py
def share_data(request):
    return {
        'auth': {
            'user': request.user.username if request.user.is_authenticated else None,
        },
    }
```

Then reference it in your settings:

```python
CROSS_INERTIA = {
    'SHARE': 'myapp.inertia.share_data',
}
```

## Flash Data and URL Fragments

Inertia v3 flash data belongs on the top-level page object, rather than in
shared props. Pass it to `render()` on the request that delivers the next page:

```python
from cross_inertia.django import render

def dashboard(request):
    return render(
        request,
        'Dashboard',
        flash=request.session.pop('inertia_flash', None),
        preserve_fragment=True,
    )
```

For the common POST-redirect-GET flow, store the flash mapping in the Django
session before returning the redirect, then pop it in the destination view as
shown above. Cross-Inertia does not currently provide a redirect-persistent
flash helper.

## External Redirects

For redirects to external URLs (or forcing a full page reload):

```python
from cross_inertia.django import location

def logout(request):
    # ... logout logic ...
    return location('https://example.com/logged-out')
```

## Automatic Dev Server Startup

When using Django's `runserver`, the middleware starts the Vite dev server automatically:

```bash
python manage.py runserver
# Vite dev server starts automatically!
```

In development mode (`DEBUG=True`), Vite also handles SSR via its `/__inertia_ssr` endpoint.
In production, supervise the standalone SSR process alongside Django and point
`SSR_URL` at it. The middleware only manages subprocesses while Django's
`runserver` command is serving requests.

The middleware runs `VITE_COMMAND` with `--port <port>` appended (a free port
by default) and waits for `http://<VITE_HOST>:<port><VITE_BASE>@vite/client` to
answer. The chosen URL is exported to Vite as `INERTIA_VITE_URL`, so
`vite.config` should use it as `server.origin` instead of hard-coding a port:

```ts
export default defineConfig({
  // ...
  server: {
    origin: process.env.INERTIA_VITE_URL,
    strictPort: true,
  },
})
```

Two more things to keep in mind:

- The command must accept a trailing `--port` (for example
  `'VITE_COMMAND': 'bun run --cwd frontend dev'`; `bun --cwd frontend run dev`
  rejects flags placed after the script name).
- To run Vite yourself in a second terminal, set a fixed `VITE_PORT`. With
  `VITE_PORT: 'auto'`, Cross-Inertia deliberately picks a free port rather than
  attaching to an arbitrary process that already occupies Vite's default port.
- If `vite.config` sets `base` (common when Django serves the built assets from
  `/static/build/`), set `VITE_BASE` to the same value or Vite will never look
  healthy and the injected script tags will 404. Alternatively keep the base for
  production builds only:

  ```ts
  export default defineConfig(({ command }) => ({
    base: command === "build" ? "/static/build/" : "/",
    // ...
  }))
  ```

If Vite fails to start, the error printed by `runserver` includes the resolved
command, the health-check URL and the last lines of Vite's output.

## URL Configuration

Add your Inertia views to your URL configuration:

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

## Full Example

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'cross_inertia.django',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cross_inertia.django.InertiaMiddleware',
]

CROSS_INERTIA = {
    'LAYOUT': 'base.html',
    'VITE_ENTRY': 'frontend/app.tsx',
    'VITE_PORT': 'auto',
}

# views.py
from cross_inertia.django import render
from cross_inertia import optional

def home(request):
    return render(request, 'Home', {
        'message': 'Hello from Django!',
        'items': optional(lambda: list(Item.objects.values())),
    })

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
]
```
