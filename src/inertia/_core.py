from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Annotated, Any

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


def read_vite_entry_from_config(vite_config_path: str = "vite.config.ts") -> str | None:
    """
    Attempt to read the Vite entry point from vite.config.ts/js.
    Returns None if not found.
    """
    config_path = Path(vite_config_path)
    if not config_path.exists():
        # Try .js extension
        config_path = Path(vite_config_path.replace(".ts", ".js"))
        if not config_path.exists():
            return None

    try:
        content = config_path.read_text()
        # Look for input: "path/to/entry"
        match = re.search(r'input:\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    except Exception as e:
        logger.debug(f"Could not read Vite config: {e}")

    return None


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

    def back(
        self, errors: dict[str, str] | None = None
    ) -> JSONResponse | HTMLResponse | Response:
        """Redirect back with errors (for form validation)"""
        # Get the referring component from the request headers or props
        # For simplicity, we'll just re-render with errors
        # In a real implementation, you'd track the previous component
        return self.response.render(
            self.request,
            self.adapter,
            self.adapter.headers.get("X-Inertia-Component", "Home"),
            {},
            errors,
            encrypt_history=self._encrypt_history,
            clear_history=self._clear_history,
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
        vite_entry: str | None = None,
        vite_config_path: str = "vite.config.ts",
    ):
        self.vite_dev_url = vite_dev_url
        self.manifest_path = manifest_path
        self._is_dev: bool | None = None
        self._manifest: dict[str, Any] | None = None
        self._shared_data: dict[str, Any] = {}  # Store shared data

        # Auto-detect vite entry from config if not provided
        if vite_entry is None:
            detected_entry = read_vite_entry_from_config(vite_config_path)
            if detected_entry:
                logger.info(f"Auto-detected Vite entry from config: {detected_entry}")
                self.vite_entry = detected_entry
            else:
                # Fallback to default
                logger.warning(
                    "Could not auto-detect Vite entry, using default: frontend/app.tsx"
                )
                self.vite_entry = "frontend/app.tsx"
        else:
            self.vite_entry = vite_entry

        # Initialize Jinja2 with custom functions
        self.templates = Jinja2Templates(directory=template_dir)
        # Add the vite() function to the Jinja2 environment
        self.templates.env.globals["vite"] = self._vite_template_function

    def is_inertia_request(self, adapter: StarletteRequestAdapter) -> bool:
        """Check if request is an Inertia XHR request"""
        return adapter.headers.get("X-Inertia") == "true"

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
        """Load Vite manifest for production builds"""
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
            logger.warning(
                f"Vite manifest not found at {self.manifest_path} - no built assets available"
            )
            self._manifest = {}

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
        # Extract path from full URL (lia returns full URL like http://testserver/test)
        from urllib.parse import urlparse
        from starlette.responses import Response

        parsed_url = urlparse(adapter.url)
        url_path = url if url is not None else parsed_url.path

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

        if partial_component == component and (partial_data or partial_except):
            if partial_data:
                # Only include requested props, but ALWAYS include shared data
                requested_keys = [key.strip() for key in partial_data.split(",")]
                # Filter to requested page props only
                filtered_props = {
                    key: props[key] for key in requested_keys if key in props
                }
                # Merge: shared data first, then filtered page props (page props override)
                props = {**shared_data, **filtered_props}
                logger.info(
                    f"Partial reload: requested props {requested_keys} + shared data {list(shared_data.keys())} for {component}"
                )
            elif partial_except:
                # Exclude specified props, but NEVER exclude shared data
                except_keys = [key.strip() for key in partial_except.split(",")]
                shared_data_keys = set(shared_data.keys())
                # Keep props that are NOT in except list OR are shared data
                filtered_props = {
                    key: val
                    for key, val in props.items()
                    if key not in except_keys or key in shared_data_keys
                }
                # Merge: shared data first, then filtered page props
                props = {**shared_data, **filtered_props}
                logger.info(
                    f"Partial reload: excluding props {except_keys} (preserving shared data) for {component}"
                )
        else:
            # No partial reload - merge all shared data with page props
            if shared_data:
                # Page props override shared data
                props = {**shared_data, **props}
                logger.debug(
                    f"Merged shared data keys {list(shared_data.keys())} with page props"
                )

        # Add errors to props (Inertia checks page.props.errors for validation errors)
        if errors:
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
        if merge_props:
            page_data["mergeProps"] = merge_props
        if prepend_props:
            page_data["prependProps"] = prepend_props
        if deep_merge_props:
            page_data["deepMergeProps"] = deep_merge_props
        if match_props_on:
            page_data["matchPropsOn"] = match_props_on
        if scroll_props:
            page_data["scrollProps"] = scroll_props

        if self.is_inertia_request(adapter):
            # Return JSON response for Inertia XHR requests
            # Always return 200 OK for Inertia requests, even with validation errors
            # Errors are communicated via props.errors, not HTTP status codes
            logger.info(f"→ Inertia XHR: {component} (props: {list(props.keys())})")
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
            template_context = {
                "request": request,
                "page": page_json,
                "vite_tags": self.get_vite_tags(),  # Backward compatibility
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
    """Get or create the singleton InertiaResponse instance"""
    global _inertia_response
    if _inertia_response is None:
        _inertia_response = InertiaResponse()
        logger.info("Inertia module initialized")
    return _inertia_response


def get_inertia(request: Request) -> Inertia:
    """FastAPI dependency to get request-scoped Inertia renderer"""
    adapter = StarletteRequestAdapter(request)
    return Inertia(request, adapter, get_inertia_response())


# Type alias for dependency injection
InertiaDep = Annotated[Inertia, Depends(get_inertia)]
