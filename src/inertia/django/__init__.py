"""
Django-specific Inertia.js adapter exports.

This module provides Django integration for Inertia.js, allowing you to build
modern single-page applications using Django as your backend.

Example usage:

    # In views.py
    from inertia.django import render, optional

    def home(request):
        return render(request, 'Home', {
            'message': 'Hello World',
            'items': list(Item.objects.values()),
        })

    # Or with decorator
    from inertia.django import inertia

    @inertia('Home')
    def home(request):
        return {'message': 'Hello World'}

    # In settings.py
    INSTALLED_APPS = [
        ...
        'inertia.django',  # For template tags
    ]

    MIDDLEWARE = [
        ...
        'inertia.django.InertiaMiddleware',
    ]

    # Optional: Configure shared data
    INERTIA_SHARE = 'myapp.inertia.share_data'

    # Optional: Configure Inertia settings
    INERTIA_LAYOUT = 'app.html'  # Default template

Template tags:
    {% load inertia %}
    <!DOCTYPE html>
    <html>
    <head>
        {% vite %}
    </head>
    <body>
        <div id="app" data-page='{{ page }}'></div>
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
from .._props import optional, always, defer
from .._config import configure_inertia

__all__ = [
    # Middleware
    "InertiaMiddleware",
    # Rendering
    "render",
    "location",
    "inertia",
    "InertiaViewMixin",
    "get_inertia_response",
    # Prop wrappers
    "optional",
    "always",
    "defer",
    # Configuration
    "configure_inertia",
]
