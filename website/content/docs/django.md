---
title: Django
description: Use Cross-Inertia with Django.
order: 2.5
section: Getting Started
---

Cross-Inertia provides full Django support with a familiar API that follows Django conventions.

## Installation

Install Cross-Inertia:

```bash
pip install cross-inertia
```

## Configuration

Add `inertia.django` to your installed apps and middleware:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'inertia.django',
]

MIDDLEWARE = [
    # ...
    'inertia.django.InertiaMiddleware',
]
```

Configure Inertia using the `CROSS_INERTIA` settings dict (similar to Django REST Framework):

```python
# settings.py

CROSS_INERTIA = {
    'LAYOUT': 'base.html',              # Template for initial page loads
    'VITE_ENTRY': 'src/main.tsx',       # Vite entry point
    'VITE_PORT': 5173,                  # Vite dev server port (or 'auto')
    'MANIFEST_PATH': 'static/build/.vite/manifest.json',
    'SSR_ENABLED': False,
    'SHARE': 'myapp.inertia.share_data',  # Dotted path to share function
}
```

All settings are optional and have sensible defaults.

## Creating Views

### Using `render()`

The simplest way to render Inertia pages:

```python
# views.py
from inertia.django import render

def home(request):
    return render(request, 'Home', {
        'message': 'Hello World',
        'user': request.user.username,
    })
```

### Using the `@inertia` decorator

For cleaner views that just return props:

```python
from inertia.django import inertia

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
from inertia.django import InertiaViewMixin

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
- `{% inertia_body %}` - Outputs the app container div with page data

## Prop Types

Use prop wrappers from the main `inertia` package (they're framework-agnostic):

```python
from inertia import optional, always, defer
from inertia.django import render

def dashboard(request):
    return render(request, 'Dashboard', {
        'user': get_user(request),                    # Regular prop
        'permissions': optional(get_permissions),     # Only when requested
        'flash': always(get_flash_messages),          # Always included
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
        'flash': request.session.pop('flash', None),
    }
```

Then reference it in your settings:

```python
CROSS_INERTIA = {
    'SHARE': 'myapp.inertia.share_data',
}
```

## External Redirects

For redirects to external URLs (or forcing a full page reload):

```python
from inertia.django import location

def logout(request):
    # ... logout logic ...
    return location('https://example.com/logged-out')
```

## Automatic Vite Startup

When using Django's `runserver`, the Vite dev server starts automatically:

```bash
python manage.py runserver
# Vite dev server starts automatically!
```

This is controlled by the app configuration and only runs in development mode.

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
    'inertia.django',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'inertia.django.InertiaMiddleware',
]

CROSS_INERTIA = {
    'LAYOUT': 'base.html',
    'VITE_ENTRY': 'frontend/app.tsx',
    'VITE_PORT': 'auto',
}

# views.py
from inertia.django import render
from inertia import optional

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
