from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import json
import logging
from pathlib import Path
from typing import Annotated, Any

import httpx
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import pass_context
from starlette.responses import Response
from fastapi.templating import Jinja2Templates
from cross_web import StarletteRequestAdapter

from ._props import optional, always, defer, once
from ._assets import build_asset_url, resolve_manifest_entry
from ._exceptions import ManifestNotFoundError
from ._page import (
    PageRenderOptions,
    build_page_request_context,
    build_inertia_page,
    is_inertia_request_headers,
    is_prefetch_request_headers,
    render_inertia_body,
)

# Configure logging with basic config if not already configured
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    force=False,  # Don't override if already configured
)

logger = logging.getLogger(__name__)
VITE_DEV_SSR_ENDPOINT = "/__inertia_ssr"


__all__ = ["optional", "always", "defer", "once", "ManifestNotFoundError"]


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
        self._flash: dict[str, Any] = {}
        self._preserve_fragment = False

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
            flash=self._flash or None,
            preserve_fragment=self._preserve_fragment,
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

    def flash(self, key: str, value: Any) -> "Inertia":
        """
        Set flash data for the current response.

        Flash data is one-time notification data (toasts, highlights) that is
        NOT persisted in browser history state. The client clears flash data
        before pushing the page to history.

        Args:
            key: The flash data key
            value: The flash data value

        Returns:
            Self for method chaining

        Example:
            @app.post("/users")
            async def create_user(inertia: InertiaDep):
                user = create_user(...)
                inertia.flash("success", "User created successfully!")
                return inertia.render("Users/Show", {"user": user})
        """
        self._flash[key] = value
        return self

    def preserve_fragment(self, preserve: bool = True) -> "Inertia":
        """
        Preserve the URL fragment (hash) across the redirect.

        When enabled, the Inertia client will keep the current URL fragment
        when navigating to this page response.

        Args:
            preserve: Whether to preserve the fragment (default: True)

        Returns:
            Self for method chaining

        Example:
            @app.post("/settings")
            async def update_settings(inertia: InertiaDep):
                save_settings(...)
                inertia.preserve_fragment()
                return inertia.render("Settings", {...})
        """
        self._preserve_fragment = preserve
        return self

    def redirect(self, url: str) -> Response:
        """
        Perform an internal redirect that preserves URL fragments.

        Unlike location() which triggers a full page reload, redirect()
        returns a 409 with X-Inertia-Redirect header that the client
        treats as an internal Inertia visit, preserving SPA state.

        Use this when redirecting to a URL that contains a fragment (#).

        Args:
            url: The URL to redirect to (should contain a fragment)

        Returns:
            Response with 409 status code and X-Inertia-Redirect header

        Example:
            return inertia.redirect("/settings#notifications")
        """
        logger.info(f"Fragment redirect to: {url}")
        return Response(
            status_code=409,
            headers={
                "X-Inertia-Redirect": url,
            },
        )


class InertiaResponse:
    """Core Inertia protocol implementation"""

    def __init__(
        self,
        template_dir: str | None = None,
        vite_dev_url: str | None = None,
        manifest_path: str | None = None,
        vite_entry: str | None = None,
        ssr_url: str | None = None,
        ssr_enabled: bool | None = None,
        asset_url_prefix: str | None = None,
    ):
        # Import here to avoid circular imports
        from cross_inertia._config import get_config

        config = get_config()
        self.vite_dev_url = vite_dev_url or config.vite_dev_url
        self.manifest_path = manifest_path or config.manifest_path
        self.asset_url_prefix = asset_url_prefix or config.asset_url_prefix
        self._is_dev: bool | None = None
        self._manifest: dict[str, Any] | None = None
        self._shared_data: dict[str, Any] = {}  # Store shared data

        # SSR configuration
        self.ssr_enabled = (
            ssr_enabled if ssr_enabled is not None else config.ssr_enabled
        )
        self.ssr_url = ssr_url or config.ssr_url
        self._ssr_client: "InertiaSSR | None" = None
        self._vite_dev_ssr_client: "InertiaSSR | None" = None
        if self.ssr_enabled:
            from cross_inertia._ssr import InertiaSSR

            self._ssr_client = InertiaSSR(url=self.ssr_url, enabled=True)
            logger.info(f"SSR enabled: {self.ssr_url}")

        self.vite_entry = vite_entry or config.vite_entry
        logger.info(f"Vite entry: {self.vite_entry}")

        # Initialize Jinja2 with custom functions
        self.templates = Jinja2Templates(directory=template_dir or config.template_dir)
        # Add template functions to the Jinja2 environment
        self.templates.env.globals["vite"] = self._vite_template_function
        self.templates.env.globals["inertia_head"] = self._make_inertia_head_function()
        self.templates.env.globals["inertia_body"] = self._make_inertia_body_function()

    def is_inertia_request(self, adapter: StarletteRequestAdapter) -> bool:
        """Check if request is an Inertia XHR request"""
        return is_inertia_request_headers(adapter.headers)

    def is_prefetch_request(self, adapter: StarletteRequestAdapter) -> bool:
        """Check if request is an Inertia prefetch request.

        Prefetch requests are Inertia XHR requests that include the
        Purpose: prefetch header. The Inertia client sends this header
        when prefetching pages in the background to improve perceived
        performance.

        Reference:
            https://inertiajs.com/prefetching
        """
        return is_prefetch_request_headers(adapter.headers)

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

    def _make_inertia_head_function(self) -> Any:
        """Create the inertia_head template function with access to self."""
        response = self

        @pass_context
        def inertia_head(context: dict) -> str:
            """
            Generate all head content needed for Inertia.

            Includes Vite script/style tags and SSR head content if present.

            Usage: {{ inertia_head() }}
            """
            parts = [response.get_vite_tags()]

            # Add SSR head tags if present
            head = context.get("head")
            if head:
                if isinstance(head, list):
                    parts.extend(head)
                else:
                    parts.append(str(head))

            return "\n".join(parts)

        return inertia_head

    def _make_inertia_body_function(self) -> Any:
        """Create the inertia_body template function."""

        @pass_context
        def inertia_body(context: dict) -> str:
            """
            Generate the Inertia app container.

            Renders the initial page JSON script and app container, or passes
            through the SSR body when server rendering is enabled.

            Usage: {{ inertia_body() }}
            """
            page = context.get("page", "{}")
            body = context.get("body", "")

            return render_inertia_body(page, body)

        return inertia_body

    def get_ssr_client(self):
        """Return the appropriate SSR client for the current runtime mode."""
        if not self.ssr_enabled:
            return None

        if self.is_dev_mode():
            if self._vite_dev_ssr_client is not None:
                return self._vite_dev_ssr_client

            from cross_inertia._ssr import InertiaSSR

            if self._ssr_client is not None and not isinstance(
                self._ssr_client, InertiaSSR
            ):
                return self._ssr_client

            self._vite_dev_ssr_client = InertiaSSR(
                url=self.vite_dev_url,
                enabled=True,
                render_path=VITE_DEV_SSR_ENDPOINT,
                health_path=VITE_DEV_SSR_ENDPOINT,
            )
            return self._vite_dev_ssr_client

        return self._ssr_client

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
            resolved_key, entry = resolve_manifest_entry(manifest, self.vite_entry)

            if not entry:
                logger.error(
                    f"No entry found for '{self.vite_entry}' in manifest - did you run 'npm run build'?"
                )
                return ""

            tags = []

            # Add CSS files
            css_files = entry.get("css", [])
            if css_files:
                logger.info(
                    f"Generating PRODUCTION script tags - {len(css_files)} CSS file(s), entry: {resolved_key or entry.get('file', 'none')}"
                )
            for css in css_files:
                tags.append(
                    f'<link rel="stylesheet" href="{build_asset_url(self.asset_url_prefix, css)}">'
                )

            # Add main JS file
            if "file" in entry:
                tags.append(
                    f'<script type="module" src="{build_asset_url(self.asset_url_prefix, entry["file"])}"></script>'
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
        flash: dict[str, Any] | None = None,
        preserve_fragment: bool = False,
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
        build_result = build_inertia_page(
            build_page_request_context(
                adapter=adapter,
                shared_data=getattr(request.state, "inertia_shared", {}),
                asset_version=self.get_asset_version(),
                url=url,
            ),
            PageRenderOptions(
                component=component,
                props=props,
                errors=errors,
                encrypt_history=encrypt_history,
                clear_history=clear_history,
                flash=flash,
                preserve_fragment=preserve_fragment,
                merge_props=merge_props,
                prepend_props=prepend_props,
                deep_merge_props=deep_merge_props,
                match_props_on=match_props_on,
                scroll_props=scroll_props,
            ),
        )

        if build_result.version_conflict_location is not None:
            logger.info(
                "Asset version mismatch detected for GET Inertia request. Returning 409 to force reload."
            )
            return Response(
                status_code=409,
                headers={"X-Inertia-Location": build_result.version_conflict_location},
            )

        assert build_result.page_data is not None
        assert build_result.page_json is not None

        if build_result.is_inertia:
            # Return JSON response for Inertia XHR requests
            # Always return 200 OK for Inertia requests, even with validation errors
            # Errors are communicated via props.errors, not HTTP status codes
            request_type = "Prefetch" if build_result.is_prefetch else "Inertia XHR"
            logger.info(
                f"→ {request_type}: {component} (props: {list(build_result.page_data['props'].keys())})"
            )
            return JSONResponse(
                content=build_result.page_data,
                headers={
                    "X-Inertia": "true",
                    "Vary": "X-Inertia",
                },
                status_code=200,
            )
        else:
            # Return HTML response for initial page load
            logger.info(
                f"→ Initial page load: {component} (props: {list(build_result.page_data['props'].keys())})"
            )

            # Try SSR if enabled
            head: list[str] = []
            body: str = ""
            ssr_client = self.get_ssr_client()
            if ssr_client:
                try:
                    # Run SSR render (need to handle sync context)
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, create a task
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run,
                                ssr_client.render(build_result.page_data),
                            )
                            ssr_result = future.result(timeout=5.0)
                    else:
                        ssr_result = loop.run_until_complete(
                            ssr_client.render(build_result.page_data)
                        )

                    if ssr_result:
                        head = ssr_result.head
                        body = ssr_result.body
                        logger.info(f"SSR rendered {component} successfully")
                except Exception as e:
                    logger.warning(f"SSR failed, falling back to CSR: {e}")

            template_context = {
                "request": request,
                "page": build_result.page_json,
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
                request,
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
        from cross_inertia._config import get_config

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
