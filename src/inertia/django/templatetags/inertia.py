"""Inertia template tags for Django templates.

Usage:
    {% load inertia %}

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>My App</title>
        {% inertia_head %}
    </head>
    <body>
        {% inertia_body %}
    </body>
    </html>
"""

from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def inertia_head(context: dict) -> SafeString:
    """
    Generate all head content needed for Inertia.

    This includes:
    - Vite script and style tags (dev server or production manifest)
    - SSR head tags if SSR is enabled

    Returns:
        HTML string with all head content

    Example:
        {% load inertia %}

        <head>
            <title>My App</title>
            {% inertia_head %}
        </head>
    """
    from inertia.django.shortcuts import get_inertia_response

    response = get_inertia_response()
    parts = [response.get_vite_tags()]

    # Add SSR head tags if present
    ssr_head = context.get("ssr_head")
    if ssr_head:
        if isinstance(ssr_head, list):
            parts.extend(ssr_head)
        else:
            parts.append(str(ssr_head))

    return mark_safe("\n".join(parts))  # type: ignore[return-value]


@register.simple_tag(takes_context=True)
def inertia_body(context: dict) -> SafeString:
    """
    Generate the Inertia app container.

    This renders:
    - The app div with data-page attribute containing page data
    - SSR body content inside the div if SSR is enabled

    Returns:
        HTML string with the app container

    Example:
        {% load inertia %}

        <body>
            {% inertia_body %}
        </body>
    """
    page = context.get("page", "{}")
    ssr_body = context.get("ssr_body", "")

    return mark_safe(f"<div id=\"app\" data-page='{page}'>{ssr_body}</div>")  # type: ignore[return-value]
