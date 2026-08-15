"""
Django-specific Inertia.js adapter exports.

This module provides Django integration for Inertia.js, allowing you to build
modern single-page applications using Django as your backend.

Example usage:

    # In settings.py
    INSTALLED_APPS = [
        ...
        'cross_inertia.django',
    ]

    MIDDLEWARE = [
        ...
        'cross_inertia.django.InertiaMiddleware',
    ]

    # Configure Inertia (all settings are optional)
    CROSS_INERTIA = {
        'LAYOUT': 'base.html',           # Template for initial page loads
        'VITE_ENTRY': 'frontend/app.tsx',  # Vite entry point
        'VITE_PORT': 'auto',              # Free port, or a fixed port number
        'MANIFEST_PATH': 'static/build/.vite/manifest.json',
        'SSR_ENABLED': False,            # Enable for server-side rendering
        'SHARE': 'myapp.inertia.share_data',  # Shared data for all pages
    }

    # In views.py
    from cross_inertia.django import render
    from cross_inertia import optional  # Prop wrappers are framework-agnostic

    def home(request):
        return render(request, 'Home', {
            'message': 'Hello World',
            'lazy_items': optional(lambda: list(Item.objects.values())),
        })

    # Or with decorator
    from cross_inertia.django import inertia

    @inertia('Home')
    def home(request):
        return {'message': 'Hello World'}

Template example:
    {% load inertia %}
    <!DOCTYPE html>
    <html>
    <head>
        {% inertia_head %}
    </head>
    <body>
        {% inertia_body %}
    </body>
    </html>
"""

from .middleware import InertiaMiddleware
from .shortcuts import (
    render,
    location,
    inertia,
    InertiaViewMixin,
    get_inertia_response,
)

__all__ = [
    # Middleware
    "InertiaMiddleware",
    # Rendering
    "render",
    "location",
    "inertia",
    "InertiaViewMixin",
    "get_inertia_response",
]
