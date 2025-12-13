from __future__ import annotations

import asyncio
import inspect
import json
import logging
from pathlib import Path
from typing import Annotated, Any, Callable

import httpx
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import Response
from fastapi.templating import Jinja2Templates
from lia import StarletteRequestAdapter

# Configure logging with basic config if not already configured
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    force=False,  # Don't override if already configured
)

logger = logging.getLogger(__name__)


class ManifestNotFoundError(Exception):
    """Raised when the Vite manifest file is not found in production mode."""

    pass


class optional:
    """
    Mark a prop as optional - only evaluated when explicitly requested.

    Works like functools.partial - you can pass args and kwargs that will be
    applied when the prop is evaluated.

    Optional props are excluded from initial page loads. They are only included
    and evaluated when requested via partial reloads with `only: ['prop_name']`.

    This is useful for expensive queries that users may not always need.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            user = get_current_user()
            return inertia.render("Dashboard", {
                "user": user,
                # These are only loaded when explicitly requested
                "permissions": optional(get_permissions, user.id),
                "activity": optional(get_activity, user_id=user.id, limit=100),
                "billing": optional(get_billing_history, user.id),
            })

        # Frontend - load optional prop on demand:
        router.reload({ only: ['permissions'] })

        # Load multiple:
        router.reload({ only: ['permissions', 'activity'] })
    """

    # TODO: Add proper typing with ParamSpec and TypeVar for better IDE support
    def __init__(self, callback: Callable[..., Any], *args: Any, **kwargs: Any):
        """
        Create an optional prop.

        Args:
            callback: A callable that returns the prop value when invoked.
            *args: Positional arguments to pass to the callback.
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("optional() requires a callable")
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)


class always:
    """
    Mark a prop as always included - even during partial reloads.

    Props wrapped with always() are always included in every Inertia response,
    even during partial reloads when only specific props are requested.

    Works like functools.partial - you can pass args and kwargs, or just a value.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            return inertia.render("Dashboard", {
                "user": get_user(),
                "flash": always(get_flash_messages),  # Always included
                "notifications": always(get_notifications, user_id=user.id),
            })

        # Frontend partial reload - flash is STILL included:
        router.reload({ only: ['user'] })  # flash is also returned
    """

    def __init__(self, value_or_callback: Any, *args: Any, **kwargs: Any):
        """
        Create an always prop.

        Args:
            value_or_callback: A value or callable that returns the prop value.
            *args: Positional arguments to pass to the callback (if callable).
            **kwargs: Keyword arguments to pass to the callback (if callable).
        """
        self.value_or_callback = value_or_callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Get the value, invoking the callback if needed."""
        if callable(self.value_or_callback):
            return self.value_or_callback(*self.args, **self.kwargs)
        return self.value_or_callback


class defer:
    """
    Mark a prop as deferred - loaded after the initial page render.

    Deferred props are excluded from the initial page load and loaded in a
    subsequent request after the page renders. This improves perceived performance
    by allowing the page to display immediately while slower data loads in the
    background.

    Unlike optional() props which require explicit requests from the frontend,
    deferred props are automatically loaded by the Inertia client after mount.

    Props can be grouped together to be loaded in the same request by providing
    a group name. Props in different groups are loaded in parallel.

    Example:
        @app.get("/dashboard")
        async def dashboard(inertia: InertiaDep):
            user = get_current_user()
            return inertia.render("Dashboard", {
                "user": user,  # Loaded immediately
                # These are loaded after page renders:
                "analytics": defer(get_analytics),  # Default group
                "notifications": defer(get_notifications, user.id),  # Default group
                # Load permissions separately (parallel with default group):
                "permissions": defer(get_permissions, user.id, group="permissions"),
            })

        # Frontend - use the Deferred component:
        <Deferred data="analytics" fallback={<Loading />}>
            <AnalyticsChart analytics={analytics} />
        </Deferred>

    Reference:
        https://inertiajs.com/deferred-props
    """

    def __init__(
        self,
        callback: Callable[..., Any],
        *args: Any,
        group: str = "default",
        **kwargs: Any,
    ):
        """
        Create a deferred prop.

        Args:
            callback: A callable that returns the prop value when invoked.
            *args: Positional arguments to pass to the callback.
            group: Name of the group for batching requests. Props in the same
                   group are loaded together; different groups load in parallel.
                   Defaults to "default".
            **kwargs: Keyword arguments to pass to the callback.
        """
        if not callable(callback):
            raise ValueError("defer() requires a callable")
        self.callback = callback
        self.args = args
        self.group = group
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """Invoke the callback with stored args/kwargs to get the value."""
        return self.callback(*self.args, **self.kwargs)


def _is_optional_prop(value: Any) -> bool:
    """Check if a value is an optional prop (excluded on initial load)."""
    return isinstance(value, optional)


def _is_always_prop(value: Any) -> bool:
    """Check if a value is an always prop (included even on partial reloads)."""
    return isinstance(value, always)


def _is_deferred_prop(value: Any) -> bool:
    """Check if a value is a deferred prop (loaded after initial render)."""
    return isinstance(value, defer)


# Keep old function name for internal compatibility
def _is_lazy_prop(value: Any) -> bool:
    """Check if a value is an optional/lazy prop."""
    return _is_optional_prop(value)


def _is_callable_prop(value: Any) -> bool:
    """Check if a value is a callable prop (function/lambda, not a class or special prop)."""
    return (
        callable(value)
        and not inspect.isclass(value)
        and not _is_optional_prop(value)
        and not _is_always_prop(value)
        and not _is_deferred_prop(value)
    )


async def _resolve_callable(value: Any) -> Any:
    """Resolve a callable value, handling both sync and async callables.

    Works with both lazy props and regular callables. Both are invoked the same
    way - lazy props have a __call__ method that invokes their callback.
    """
    result = value()
    if inspect.iscoroutine(result):
        return await result
    return result


async def _resolve_props(props: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively resolve all callable props in a dictionary.

    Supports:
    - Top-level callable props: {"user": lambda: get_user()}
    - Nested callable props: {"data": {"user": lambda: get_user()}}
    - Lists with callable props: {"items": [lambda: get_item(1), lambda: get_item(2)]}
    - Async callables: {"user": async_get_user}

    Non-callable values are passed through unchanged.
    """
    resolved: dict[str, Any] = {}

    for key, value in props.items():
        resolved[key] = await _resolve_value(value)

    return resolved


async def _resolve_value(value: Any) -> Any:
    """Resolve a single value, which may be callable, optional, always, defer, dict, or list."""
    if _is_optional_prop(value):
        return await _resolve_callable(value)
    elif _is_always_prop(value):
        return await _resolve_callable(value)
    elif _is_deferred_prop(value):
        return await _resolve_callable(value)
    elif _is_callable_prop(value):
        return await _resolve_callable(value)
    elif isinstance(value, dict):
        return await _resolve_props(value)
    elif isinstance(value, list):
        return [await _resolve_value(item) for item in value]
    else:
        return value


def _resolve_props_sync(props: dict[str, Any]) -> dict[str, Any]:
    """
    Synchronous wrapper for resolving callable props.
    Uses asyncio.run() to execute the async resolution.
    """
    try:
        # Try to get the running loop
        asyncio.get_running_loop()
        # If we're already in an async context, we need to handle this differently
        # Create a new task in the existing loop
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _resolve_props(props))
            return future.result()
    except RuntimeError:
        # No running loop, we can use asyncio.run directly
        return asyncio.run(_resolve_props(props))


class Inertia:
    """Request-scoped Inertia renderer"""

    def __init__(
        self,
        request: Request,
        adapter: StarletteRequestAdapter,
        response: InertiaResponse,
    ):
        self.request = request
        self.adapter = adapter
        self.response = response
        self._encrypt_history = False
        self._clear_history = False

    def render(
        self,
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
    ) -> JSONResponse | HTMLResponse | Response:
        """Render an Inertia response without needing to pass request

        Args:
            url: Optional URL to use instead of the current request URL.
                 Useful for rendering a component with a different URL than the endpoint.
            scroll_props: Configuration for infinite scroll prop merging behavior.
            view_data: Optional extra data to pass to the template (not included in page props).
                      Useful for server-side meta tags, page titles, etc.
        """
        if props is None:
            props = {}
        return self.response.render(
            self.request,
            self.adapter,
            component,
            props,
            errors,
            encrypt_history=self._encrypt_history,
            clear_history=self._clear_history,
            merge_props=merge_props,
            prepend_props=prepend_props,
            deep_merge_props=deep_merge_props,
            match_props_on=match_props_on,
            scroll_props=scroll_props,
            url=url,
            view_data=view_data,
        )

    def location(self, url: str) -> Response:
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
            Response with 409 status code and X-Inertia-Location header

        Example:
            # Redirect to OAuth provider
            return inertia.location("https://github.com/login/oauth/authorize?...")

            # Redirect to Google Maps
            return inertia.location(f"https://maps.google.com/?q={address}")

            # Redirect to payment gateway
            return inertia.location(stripe_checkout_url)

        Reference:
            https://inertiajs.com/redirects#external-redirects
        """
        logger.info(f"External redirect to: {url}")
        return Response(
            status_code=409,
            headers={
                "X-Inertia-Location": url,
            },
        )

    def encrypt_history(self, encrypt: bool = True) -> "Inertia":
        """
        Enable or disable history encryption for the current page.

        When enabled, the Inertia client will encrypt the page data before
        storing it in the browser's history state. The encryption key is stored
        in sessionStorage. This protects sensitive data from being visible when
        users navigate back to the page after logging out.

        The encryption uses the browser's Web Crypto API (AES-GCM) and only
        works in secure contexts (HTTPS, except localhost).

        Args:
            encrypt: Whether to encrypt the history (default: True)

        Returns:
            Self for method chaining

        Example:
            # Banking page with sensitive data
            @app.get("/account")
            async def account(inertia: InertiaDep):
                inertia.encrypt_history()  # Enable encryption
                return inertia.render("Account", {
                    "balance": user.balance,
                    "transactions": user.transactions
                })

            # Or disable if needed
            inertia.encrypt_history(False)

        Reference:
            https://inertiajs.com/history-encryption
        """
        self._encrypt_history = encrypt
        if encrypt:
            logger.info("History encryption enabled for this page")
        return self

    def clear_history(self, clear: bool = True) -> "Inertia":
        """
        Clear encrypted history state by rotating the encryption key.

        When enabled, the Inertia client will delete the current encryption key
        from sessionStorage and generate a new one. This makes all previously
        encrypted history states unreadable, effectively clearing sensitive data
        from the browser's history.

        This is typically used on logout to ensure users cannot navigate back
        to pages with sensitive data.

        Args:
            clear: Whether to clear the history (default: True)

        Returns:
            Self for method chaining

        Example:
            # Logout endpoint
            @app.post("/logout")
            async def logout(inertia: InertiaDep):
                clear_session()
                inertia.clear_history()  # Clear all encrypted history
                return inertia.render("Login", {})

        Reference:
            https://inertiajs.com/history-encryption#clearing-history
        """
        self._clear_history = clear
        if clear:
            logger.info("History will be cleared (encryption keys rotated)")
        return self


class InertiaResponse:
    """Core Inertia protocol implementation"""

    def __init__(
        self,
        template_dir: str = "templates",
        vite_dev_url: str = "http://localhost:5173",
        manifest_path: str = "static/build/.vite/manifest.json",
        vite_entry: str = "frontend/app.tsx",
        ssr_url: str | None = None,
        ssr_enabled: bool = False,
    ):
        self.vite_dev_url = vite_dev_url
        self.manifest_path = manifest_path
        self._is_dev: bool | None = None
        self._manifest: dict[str, Any] | None = None
        self._shared_data: dict[str, Any] = {}  # Store shared data

        # SSR configuration
        self.ssr_enabled = ssr_enabled
        self.ssr_url = ssr_url or "http://127.0.0.1:13714"
        self._ssr_client: "InertiaSSR | None" = None
        if ssr_enabled:
            from inertia._ssr import InertiaSSR

            self._ssr_client = InertiaSSR(url=self.ssr_url, enabled=True)
            logger.info(f"SSR enabled: {self.ssr_url}")

        self.vite_entry = vite_entry
        logger.info(f"Vite entry: {self.vite_entry}")

        # Initialize Jinja2 with custom functions
        self.templates = Jinja2Templates(directory=template_dir)
        # Add the vite() function to the Jinja2 environment
        self.templates.env.globals["vite"] = self._vite_template_function

    def is_inertia_request(self, adapter: StarletteRequestAdapter) -> bool:
        """Check if request is an Inertia XHR request"""
        return adapter.headers.get("X-Inertia") == "true"

    def is_prefetch_request(self, adapter: StarletteRequestAdapter) -> bool:
        """Check if request is an Inertia prefetch request.

        Prefetch requests are Inertia XHR requests that include the
        Purpose: prefetch header. The Inertia client sends this header
        when prefetching pages in the background to improve perceived
        performance.

        Reference:
            https://inertiajs.com/prefetching
        """
        return (
            self.is_inertia_request(adapter)
            and adapter.headers.get("Purpose") == "prefetch"
        )

    def is_dev_mode(self) -> bool:
        """Check if Vite dev server is running"""
        if self._is_dev is not None:
            return self._is_dev

        logger.info(f"Checking Vite dev server at {self.vite_dev_url}...")
        try:
            response = httpx.get(f"{self.vite_dev_url}/@vite/client", timeout=0.1)
            self._is_dev = response.status_code == 200
            if self._is_dev:
                logger.info("✓ Vite dev server detected - running in DEVELOPMENT mode")
            else:
                logger.info(
                    f"✗ Vite dev server responded with {response.status_code} - running in PRODUCTION mode"
                )
        except Exception as e:
            self._is_dev = False
            logger.info(
                f"✗ Vite dev server not reachable ({e.__class__.__name__}) - running in PRODUCTION mode"
            )

        return self._is_dev

    def get_manifest(self) -> dict[str, Any]:
        """Load Vite manifest for production builds.

        Raises:
            ManifestNotFoundError: If the manifest file doesn't exist in production mode.
        """
        if self._manifest is not None:
            return self._manifest

        manifest_file = Path(self.manifest_path)
        if manifest_file.exists():
            logger.info(f"Loading Vite manifest from {self.manifest_path}")
            with open(manifest_file) as f:
                manifest_data: dict[str, Any] = json.load(f)
                self._manifest = manifest_data
            logger.info(f"Manifest loaded with {len(manifest_data)} entry/entries")
        else:
            raise ManifestNotFoundError(
                f"Vite manifest not found at '{self.manifest_path}'. "
                "Did you run 'vite build'? "
                "Make sure build artifacts are included in your deployment."
            )

        return self._manifest

    def get_asset_version(self) -> str:
        """Get asset version for cache busting"""
        if self.is_dev_mode():
            return "dev"

        manifest = self.get_manifest()
        # Use MD5 hash of manifest as version for deterministic, positive values
        import hashlib

        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.md5(manifest_str.encode()).hexdigest()

    def _vite_template_function(self, entry: str | None = None) -> str:
        """
        Template function for generating Vite tags.
        Can be called from Jinja2 templates as: {{ vite() }} or {{ vite('custom/entry.js') }}
        """
        if entry:
            # Temporarily override the entry
            original_entry = self.vite_entry
            self.vite_entry = entry
            result = self.get_vite_tags()
            self.vite_entry = original_entry
            return result
        return self.get_vite_tags()

    def get_vite_tags(self) -> str:
        """Generate script tags for Vite assets"""
        if self.is_dev_mode():
            # Development mode - use Vite dev server
            # React refresh preamble must come BEFORE Vite client
            logger.info(
                f"Generating DEV mode script tags (Vite server: {self.vite_dev_url})"
            )
            return f'''
                <script type="module">
                    import RefreshRuntime from "{self.vite_dev_url}/@react-refresh"
                    RefreshRuntime.injectIntoGlobalHook(window)
                    window.$RefreshReg$ = () => {{}}
                    window.$RefreshSig$ = () => (type) => type
                    window.__vite_plugin_react_preamble_installed__ = true
                </script>
                <script type="module" src="{self.vite_dev_url}/@vite/client"></script>
                <script type="module" src="{self.vite_dev_url}/{self.vite_entry}"></script>
            '''
        else:
            # Production mode - use built assets from manifest
            manifest = self.get_manifest()
            entry = manifest.get(self.vite_entry, {})

            if not entry:
                logger.error(
                    f"No entry found for '{self.vite_entry}' in manifest - did you run 'npm run build'?"
                )

            tags = []

            # Add CSS files
            css_files = entry.get("css", [])
            if css_files:
                logger.info(
                    f"Generating PRODUCTION script tags - {len(css_files)} CSS file(s), entry: {entry.get('file', 'none')}"
                )
            for css in css_files:
                tags.append(f'<link rel="stylesheet" href="/static/build/{css}">')

            # Add main JS file
            if "file" in entry:
                tags.append(
                    f'<script type="module" src="/static/build/{entry["file"]}"></script>'
                )
            else:
                logger.warning("No JS entry file found in manifest!")

            return "\n".join(tags)

    def render(
        self,
        request: Request,
        adapter: StarletteRequestAdapter,
        component: str,
        props: dict[str, Any],
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
    ) -> JSONResponse | HTMLResponse | Response:
        """
        Render an Inertia response.
        Returns JSON for Inertia requests, HTML for initial page loads.

        Args:
            url: Optional URL to use instead of the current request URL.
                 Useful for rendering a component with a different URL than the endpoint.
            view_data: Optional extra data to pass to the template (not included in page props).
                      Useful for server-side meta tags, page titles, etc.
        """
        # Extract path and query from full URL (lia returns full URL like http://testserver/test)
        from urllib.parse import urlparse
        from starlette.responses import Response

        parsed_url = urlparse(adapter.url)
        # Include query string in the URL so Inertia can update the browser's address bar
        if url is not None:
            url_path = url
        elif parsed_url.query:
            url_path = f"{parsed_url.path}?{parsed_url.query}"
        else:
            url_path = parsed_url.path

        # Check for asset version mismatch (only for Inertia requests)
        if self.is_inertia_request(adapter):
            client_version = adapter.headers.get("X-Inertia-Version")
            server_version = self.get_asset_version()

            # If client sent a version and it doesn't match, force a full page reload
            if client_version and client_version != server_version:
                logger.info(
                    f"Asset version mismatch: client={client_version}, server={server_version}. "
                    f"Returning 409 to force reload."
                )
                # Return 409 Conflict with the current URL to trigger a full page reload
                # The client will perform a full page reload to get the new assets
                return Response(
                    status_code=409,
                    headers={
                        "X-Inertia-Location": adapter.url,
                    },
                )

        # Merge shared data from middleware (if available)
        # Shared data is set by InertiaMiddleware in request.state.inertia_shared
        shared_data = getattr(request.state, "inertia_shared", {})

        # Handle partial reloads - filter props if requested
        # Only apply if component matches (partial reloads only work for same component)
        partial_component = adapter.headers.get("X-Inertia-Partial-Component")
        partial_data = adapter.headers.get("X-Inertia-Partial-Data")
        partial_except = adapter.headers.get("X-Inertia-Partial-Except")

        # Parse X-Inertia-Reset header - props that should be reset (not merged) on client
        # Used with infinite scroll to clear data when filters change
        reset_header = adapter.headers.get("X-Inertia-Reset")
        reset_props: list[str] = []
        if reset_header:
            reset_props = [
                key.strip() for key in reset_header.split(",") if key.strip()
            ]
            logger.info(f"Reset props requested: {reset_props}")

        # Track special prop types for filtering
        optional_prop_keys = {
            key for key, val in props.items() if _is_optional_prop(val)
        }
        always_prop_keys = {key for key, val in props.items() if _is_always_prop(val)}
        # Build deferred props map: {group_name: [prop_keys]}
        deferred_props_map: dict[str, list[str]] = {}
        for key, val in props.items():
            if _is_deferred_prop(val):
                group = val.group
                if group not in deferred_props_map:
                    deferred_props_map[group] = []
                deferred_props_map[group].append(key)
        deferred_prop_keys = {
            key for keys in deferred_props_map.values() for key in keys
        }

        if partial_component == component and (partial_data or partial_except):
            if partial_data:
                # Only include requested props, but ALWAYS include shared data and always() props
                requested_keys = [key.strip() for key in partial_data.split(",")]
                # Filter to requested page props only
                # Optional props and deferred props ARE included if explicitly requested
                filtered_props = {
                    key: props[key] for key in requested_keys if key in props
                }
                # Always include always() props
                always_props = {key: props[key] for key in always_prop_keys}
                # Merge: shared data first, then always props, then filtered page props
                props = {**shared_data, **always_props, **filtered_props}
                # Clear deferred props map for partial reloads - they're being resolved
                deferred_props_map = {}
                logger.info(
                    f"Partial reload: requested props {requested_keys} + shared data {list(shared_data.keys())} + always props {list(always_prop_keys)} for {component}"
                )
            elif partial_except:
                # Exclude specified props, but NEVER exclude shared data or always() props
                except_keys = [key.strip() for key in partial_except.split(",")]
                shared_data_keys = set(shared_data.keys())
                # Keep props that are NOT in except list OR are shared data OR are always()
                # Also exclude optional and deferred props (they're only included when explicitly requested)
                filtered_props = {
                    key: val
                    for key, val in props.items()
                    if (
                        key not in except_keys
                        or key in shared_data_keys
                        or key in always_prop_keys
                    )
                    and key not in optional_prop_keys
                    and key not in deferred_prop_keys
                }
                # Merge: shared data first, then filtered page props
                props = {**shared_data, **filtered_props}
                logger.info(
                    f"Partial reload: excluding props {except_keys} (preserving shared data and always props) for {component}"
                )
        else:
            # No partial reload - merge all shared data with page props
            # Exclude optional props on initial load (they must be explicitly requested)
            # Exclude deferred props on initial load (they load automatically after render)
            excluded_props = optional_prop_keys | deferred_prop_keys
            if excluded_props:
                props = {
                    key: val for key, val in props.items() if key not in excluded_props
                }
                if optional_prop_keys:
                    logger.info(
                        f"Excluding optional props from initial load: {optional_prop_keys}"
                    )
                if deferred_prop_keys:
                    logger.info(
                        f"Excluding deferred props from initial load: {deferred_prop_keys}"
                    )
            if shared_data:
                # Page props override shared data
                props = {**shared_data, **props}
                logger.debug(
                    f"Merged shared data keys {list(shared_data.keys())} with page props"
                )

        # Resolve callable props (lambdas, functions) before rendering
        # This allows lazy evaluation of expensive props
        props = _resolve_props_sync(props)

        # Add errors to props (Inertia checks page.props.errors for validation errors)
        # Check for error bag header to scope errors appropriately
        if errors:
            if error_bag := adapter.headers.get("X-Inertia-Error-Bag"):
                # Scope errors under the error bag name
                props["errors"] = {error_bag: errors}
                logger.info(
                    f"Rendering {component} with validation errors in bag '{error_bag}': {list(errors.keys())}"
                )
            else:
                props["errors"] = errors
                logger.info(
                    f"Rendering {component} with validation errors: {list(errors.keys())}"
                )

        page_data = {
            "component": component,
            "props": props,
            "url": url_path,
            "version": self.get_asset_version(),
            "encryptHistory": encrypt_history,
            "clearHistory": clear_history,
        }

        # Add optional merge/prepend props for infinite scroll support
        # Filter out reset props from merge lists - reset props should replace, not merge
        # Also filter out nested props (e.g., reset "cats" should exclude "cats.data")
        def should_exclude_from_merge(prop: str) -> bool:
            """Check if a prop should be excluded due to reset."""
            for reset_prop in reset_props:
                # Exact match
                if prop == reset_prop:
                    return True
                # Nested prop: "cats.data" starts with "cats."
                if prop.startswith(f"{reset_prop}."):
                    return True
            return False

        if merge_props:
            filtered_merge = [
                p for p in merge_props if not should_exclude_from_merge(p)
            ]
            if filtered_merge:
                page_data["mergeProps"] = filtered_merge
        if prepend_props:
            filtered_prepend = [
                p for p in prepend_props if not should_exclude_from_merge(p)
            ]
            if filtered_prepend:
                page_data["prependProps"] = filtered_prepend
        if deep_merge_props:
            filtered_deep = [
                p for p in deep_merge_props if not should_exclude_from_merge(p)
            ]
            if filtered_deep:
                page_data["deepMergeProps"] = filtered_deep
        if match_props_on:
            filtered_match = [
                p for p in match_props_on if not should_exclude_from_merge(p)
            ]
            if filtered_match:
                page_data["matchPropsOn"] = filtered_match
        if scroll_props:
            page_data["scrollProps"] = scroll_props

        # Include reset props in response so client knows which props to reset
        if reset_props:
            page_data["resetProps"] = reset_props
            logger.info(f"Including resetProps in response: {reset_props}")

        # Add deferred props map to page data (tells client what to fetch after render)
        if deferred_props_map:
            page_data["deferredProps"] = deferred_props_map
            logger.info(f"Deferred props: {deferred_props_map}")

        if self.is_inertia_request(adapter):
            # Return JSON response for Inertia XHR requests
            # Always return 200 OK for Inertia requests, even with validation errors
            # Errors are communicated via props.errors, not HTTP status codes
            is_prefetch = self.is_prefetch_request(adapter)
            request_type = "Prefetch" if is_prefetch else "Inertia XHR"
            logger.info(f"→ {request_type}: {component} (props: {list(props.keys())})")
            return JSONResponse(
                content=page_data,
                headers={
                    "X-Inertia": "true",
                    "Vary": "X-Inertia",
                },
                status_code=200,
            )
        else:
            # Return HTML response for initial page load
            logger.info(
                f"→ Initial page load: {component} (props: {list(props.keys())})"
            )
            # Escape single quotes in JSON for safe embedding in HTML attributes
            page_json = json.dumps(page_data).replace("'", "&#39;")

            # Try SSR if enabled
            head: list[str] = []
            body: str = ""
            if self._ssr_client and self.ssr_enabled:
                import asyncio

                try:
                    # Run SSR render (need to handle sync context)
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, create a task
                        import concurrent.futures

                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run, self._ssr_client.render(page_data)
                            )
                            ssr_result = future.result(timeout=5.0)
                    else:
                        ssr_result = loop.run_until_complete(
                            self._ssr_client.render(page_data)
                        )

                    if ssr_result:
                        head = ssr_result.head
                        body = ssr_result.body
                        logger.info(f"SSR rendered {component} successfully")
                except Exception as e:
                    logger.warning(f"SSR failed, falling back to CSR: {e}")

            template_context = {
                "request": request,
                "page": page_json,
                "vite_tags": self.get_vite_tags(),  # Backward compatibility
                "head": head,
                "body": body,
                # Note: vite() function is also available globally
            }
            # Add view_data to template context if provided
            if view_data:
                template_context.update(view_data)
                logger.debug(f"Adding view_data to template: {list(view_data.keys())}")
            return self.templates.TemplateResponse(
                "app.html",
                template_context,
            )


# Singleton instance - lazy loaded to avoid initialization issues during testing
_inertia_response: InertiaResponse | None = None


def get_inertia_response() -> InertiaResponse:
    """Get or create the singleton InertiaResponse instance.

    If configure_inertia() was called, this uses those settings.
    Otherwise, uses default values.
    """
    global _inertia_response
    if _inertia_response is None:
        from inertia._config import get_config

        config = get_config()
        _inertia_response = InertiaResponse(
            template_dir=config.template_dir,
            vite_dev_url=config.vite_dev_url,
            manifest_path=config.manifest_path,
            vite_entry=config.vite_entry,
            ssr_url=config.ssr_url,
            ssr_enabled=config.ssr_enabled,
        )
        logger.info("Inertia module initialized")
    return _inertia_response


def reset_inertia_response() -> None:
    """Reset the InertiaResponse singleton. Useful for testing."""
    global _inertia_response
    _inertia_response = None


def get_inertia(request: Request) -> Inertia:
    """FastAPI dependency to get request-scoped Inertia renderer"""
    adapter = StarletteRequestAdapter(request)
    return Inertia(request, adapter, get_inertia_response())


# Type alias for dependency injection
InertiaDep = Annotated[Inertia, Depends(get_inertia)]
