"""Django shortcuts for Inertia.js rendering."""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from django.http import HttpRequest, HttpResponse

from .response import DjangoInertiaResponse

logger = logging.getLogger(__name__)

# Module-level singleton
_inertia_response: DjangoInertiaResponse | None = None

F = TypeVar("F", bound=Callable[..., Any])


def get_inertia_response() -> DjangoInertiaResponse:
    """Get or create the singleton DjangoInertiaResponse instance.

    The instance is configured using Django settings (settings.CROSS_INERTIA dict).
    """
    global _inertia_response
    if _inertia_response is None:
        _inertia_response = DjangoInertiaResponse()
    return _inertia_response


def reset_inertia_response() -> None:
    """Reset the DjangoInertiaResponse singleton. Useful for testing."""
    global _inertia_response
    _inertia_response = None


def render(
    request: "HttpRequest",
    component: str,
    props: dict[str, Any] | None = None,
    errors: dict[str, str] | None = None,
    encrypt_history: bool = False,
    clear_history: bool = False,
    merge_props: list[str] | None = None,
    prepend_props: list[str] | None = None,
    deep_merge_props: list[str] | None = None,
    match_props_on: list[str] | None = None,
    scroll_props: dict[str, Any] | None = None,
    url: str | None = None,
    view_data: dict[str, Any] | None = None,
) -> "HttpResponse":
    """
    Render an Inertia response.

    This is the primary way to return Inertia responses from Django views.
    For Inertia XHR requests, returns JSON. For initial page loads, returns HTML.

    Args:
        request: The Django HttpRequest object.
        component: The frontend component name (e.g., 'Home', 'users/Show').
        props: Props to pass to the component. Supports callables, optional(),
               always(), and defer() wrappers.
        errors: Validation errors to pass to the component (added to props.errors).
        encrypt_history: Whether to encrypt the page state in browser history.
        clear_history: Whether to clear encrypted history (rotate encryption keys).
        merge_props: Props that should be merged instead of replaced on reload.
        prepend_props: Props that should be prepended instead of appended.
        deep_merge_props: Props that should be deep merged.
        match_props_on: Keys to use for matching props during merge.
        scroll_props: Scroll position configuration for props.
        url: Override the URL in the Inertia response (defaults to request URL).
        view_data: Extra data to pass to the template (not included in page props).

    Returns:
        HttpResponse (JsonResponse for XHR, TemplateResponse for initial loads)

    Example:
        from inertia.django import render

        def home(request):
            return render(request, 'Home', {
                'message': 'Hello World',
                'items': list(Item.objects.values('id', 'name')),
            })

        def dashboard(request):
            return render(request, 'Dashboard', {
                'user': lambda: get_user_data(request.user),
                'stats': optional(get_expensive_stats),
                'notifications': defer(get_notifications, group='sidebar'),
            })

        def form_submit(request):
            if form.is_valid():
                form.save()
                return redirect('success')
            return render(request, 'Form', props, errors=form.errors)
    """
    if props is None:
        props = {}

    response = get_inertia_response()
    return response.render(
        request,
        component,
        props,
        errors=errors,
        encrypt_history=encrypt_history,
        clear_history=clear_history,
        merge_props=merge_props,
        prepend_props=prepend_props,
        deep_merge_props=deep_merge_props,
        match_props_on=match_props_on,
        scroll_props=scroll_props,
        url=url,
        view_data=view_data,
    )


def location(url: str) -> "HttpResponse":
    """
    Perform an external redirect (full page navigation).

    This is used when you need to redirect to:
    - External websites (OAuth providers, payment gateways)
    - Non-Inertia pages within your app
    - Third-party services (Google Maps, file downloads, etc.)

    Returns a 409 Conflict response with X-Inertia-Location header.
    The Inertia client will automatically perform a window.location = url visit.

    Args:
        url: The URL to redirect to (can be absolute or relative)

    Returns:
        HttpResponse with 409 status code and X-Inertia-Location header

    Example:
        from inertia.django import location

        def oauth_redirect(request):
            return location('https://github.com/login/oauth/authorize?...')

        def download_file(request, file_id):
            file_url = get_signed_download_url(file_id)
            return location(file_url)

    Reference:
        https://inertiajs.com/redirects#external-redirects
    """
    logger.info(f"External redirect to: {url}")
    return HttpResponse(
        status=409,
        headers={"X-Inertia-Location": url},
    )


def inertia(component: str) -> Callable[[F], F]:
    """
    Decorator for function-based views that return props dicts.

    The decorated function should return a dict of props (or an HttpResponse
    to pass through). The decorator wraps the props in an Inertia render call.

    Args:
        component: The frontend component name (e.g., 'Home', 'users/Show')

    Returns:
        A decorator function

    Example:
        from inertia.django import inertia

        @inertia('Home')
        def home(request):
            return {'message': 'Hello World'}

        @inertia('users/List')
        def user_list(request):
            return {
                'users': list(User.objects.values('id', 'name', 'email')),
                'total': User.objects.count(),
            }

        # Pass through HttpResponse (e.g., for redirects)
        @inertia('Form')
        def form_view(request):
            if request.method == 'POST' and form.is_valid():
                form.save()
                return redirect('success')
            return {'form_data': form.initial}
    """

    def decorator(view_func: F) -> F:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            result = view_func(request, *args, **kwargs)

            # If view returns HttpResponse, pass through (for redirects, etc.)
            if isinstance(result, HttpResponse):
                return result

            # Otherwise treat as props dict
            props = result if isinstance(result, dict) else {}
            return render(request, component, props)

        return wrapper  # type: ignore

    return decorator


class InertiaViewMixin:
    """
    Mixin for class-based views to simplify Inertia rendering.

    Add this mixin to your view class and define the component attribute.
    Override get_props() to return the props for your component.

    Attributes:
        component: The frontend component name (required)

    Example:
        from django.views import View
        from inertia.django import InertiaViewMixin

        class HomeView(InertiaViewMixin, View):
            component = 'Home'

            def get_props(self, request):
                return {'message': 'Hello World'}

        class UserDetailView(InertiaViewMixin, View):
            component = 'users/Show'

            def get_props(self, request, user_id):
                user = get_object_or_404(User, pk=user_id)
                return {
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                    }
                }

            def get(self, request, user_id):
                return self.render_inertia(request)

        class FormView(InertiaViewMixin, View):
            component = 'Form'

            def get_props(self, request):
                return {'initial': {}}

            def get_errors(self, request):
                return getattr(request, '_form_errors', None)

            def get(self, request):
                return self.render_inertia(request)

            def post(self, request):
                form = MyForm(request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('success')
                request._form_errors = form.errors
                return self.render_inertia(request)
    """

    component: str = ""

    def get_props(
        self, request: "HttpRequest", *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        """Return props dict for the component.

        Override this method to provide props to your component.
        The request and any URL kwargs are passed for convenience.
        """
        return {}

    def get_errors(self, request: "HttpRequest") -> dict[str, str] | None:
        """Return validation errors dict.

        Override this method to provide validation errors.
        Returns None by default (no errors).
        """
        return None

    def get_view_data(self, request: "HttpRequest") -> dict[str, Any] | None:
        """Return extra template context data.

        Override this method to provide extra data to the template
        that should not be included in page props.
        """
        return None

    def render_inertia(
        self,
        request: "HttpRequest",
        extra_props: dict[str, Any] | None = None,
        **render_kwargs: Any,
    ) -> "HttpResponse":
        """Render the Inertia response.

        Call this from your get/post/etc methods to render the response.

        Args:
            request: The Django HttpRequest
            extra_props: Additional props to merge with get_props() result
            **render_kwargs: Additional arguments to pass to render()

        Returns:
            HttpResponse
        """
        # Get URL args from the view
        view = self  # type: ignore
        args = getattr(view, "args", ())
        kwargs = getattr(view, "kwargs", {})

        props = self.get_props(request, *args, **kwargs)
        if extra_props:
            props = {**props, **extra_props}

        errors = self.get_errors(request)
        view_data = self.get_view_data(request)

        return render(
            request,
            self.component,
            props,
            errors=errors,
            view_data=view_data,
            **render_kwargs,
        )
