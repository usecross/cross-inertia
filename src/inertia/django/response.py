"""Django-specific Inertia response handling."""

from __future__ import annotations

import json
import hashlib
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse

from .._exceptions import ManifestNotFoundError
from .conf import inertia_settings
from .._utils import (
    _is_always_prop,
    _is_deferred_prop,
    _is_optional_prop,
    _resolve_props_sync,
)

logger = logging.getLogger(__name__)


class DjangoInertiaResponse:
    """Django-specific Inertia response implementation.

    This class handles the core Inertia protocol for Django, including:
    - Detecting Inertia XHR requests
    - Asset version checking
    - Partial reloads
    - Props resolution (optional, always, defer)
    - JSON/HTML response generation
    """

    def __init__(
        self,
        template_name: str | None = None,
        vite_dev_url: str | None = None,
        manifest_path: str | None = None,
        vite_entry: str | None = None,
        ssr_enabled: bool | None = None,
        ssr_url: str | None = None,
    ):
        self.template_name = template_name or inertia_settings.LAYOUT
        self.vite_dev_url = vite_dev_url or inertia_settings.VITE_DEV_URL
        self.manifest_path = manifest_path or inertia_settings.MANIFEST_PATH
        self.vite_entry = vite_entry or inertia_settings.VITE_ENTRY
        self.ssr_enabled = (
            ssr_enabled if ssr_enabled is not None else inertia_settings.SSR_ENABLED
        )
        self.ssr_url = ssr_url or inertia_settings.SSR_URL

        self._is_dev: bool | None = None
        self._manifest: dict[str, Any] | None = None

    def is_inertia_request(self, request: "HttpRequest") -> bool:
        """Check if request is an Inertia XHR request."""
        return request.headers.get("X-Inertia") == "true"  # type: ignore[attr-defined]

    def is_prefetch_request(self, request: "HttpRequest") -> bool:
        """Check if request is an Inertia prefetch request."""
        return (
            self.is_inertia_request(request)
            and request.headers.get("Purpose") == "prefetch"  # type: ignore[attr-defined]
        )

    def is_dev_mode(self) -> bool:
        """Check if Vite dev server is running."""
        if self._is_dev is not None:
            return self._is_dev

        logger.info(f"Checking Vite dev server at {self.vite_dev_url}...")
        try:
            response = httpx.get(f"{self.vite_dev_url}/@vite/client", timeout=0.1)
            self._is_dev = response.status_code == 200
            if self._is_dev:
                logger.info("Vite dev server detected - running in DEVELOPMENT mode")
            else:
                logger.info(
                    f"Vite dev server responded with {response.status_code} - running in PRODUCTION mode"
                )
        except Exception as e:
            self._is_dev = False
            logger.info(
                f"Vite dev server not reachable ({e.__class__.__name__}) - running in PRODUCTION mode"
            )

        return self._is_dev

    def get_manifest(self) -> dict[str, Any]:
        """Load Vite manifest for production builds."""
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
        """Get asset version for cache busting."""
        if self.is_dev_mode():
            return "dev"

        manifest = self.get_manifest()
        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.md5(manifest_str.encode()).hexdigest()

    def get_vite_tags(self) -> str:
        """Generate script tags for Vite assets."""
        if self.is_dev_mode():
            logger.info(
                f"Generating DEV mode script tags (Vite server: {self.vite_dev_url})"
            )
            return f"""
                <script type="module">
                    import RefreshRuntime from "{self.vite_dev_url}/@react-refresh"
                    RefreshRuntime.injectIntoGlobalHook(window)
                    window.$RefreshReg$ = () => {{}}
                    window.$RefreshSig$ = () => (type) => type
                    window.__vite_plugin_react_preamble_installed__ = true
                </script>
                <script type="module" src="{self.vite_dev_url}/@vite/client"></script>
                <script type="module" src="{self.vite_dev_url}/{self.vite_entry}"></script>
            """
        else:
            manifest = self.get_manifest()
            entry = manifest.get(self.vite_entry, {})

            if not entry:
                logger.error(
                    f"No entry found for '{self.vite_entry}' in manifest - did you run 'npm run build'?"
                )

            tags = []

            css_files = entry.get("css", [])
            if css_files:
                logger.info(
                    f"Generating PRODUCTION script tags - {len(css_files)} CSS file(s), entry: {entry.get('file', 'none')}"
                )
            for css in css_files:
                tags.append(f'<link rel="stylesheet" href="/static/build/{css}">')

            if "file" in entry:
                tags.append(
                    f'<script type="module" src="/static/build/{entry["file"]}"></script>'
                )
            else:
                logger.warning("No JS entry file found in manifest!")

            return "\n".join(tags)

    def render(
        self,
        request: "HttpRequest",
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
    ) -> HttpResponse:
        """Render an Inertia response for Django."""
        # Extract path and query from request
        parsed_url = urlparse(request.build_absolute_uri())
        if url is not None:
            url_path = url
        elif parsed_url.query:
            url_path = f"{parsed_url.path}?{parsed_url.query}"
        else:
            url_path = parsed_url.path

        # Check for asset version mismatch (only for Inertia requests)
        if self.is_inertia_request(request):
            client_version = request.headers.get("X-Inertia-Version")  # type: ignore[attr-defined]
            server_version = self.get_asset_version()

            if client_version and client_version != server_version:
                logger.info(
                    f"Asset version mismatch: client={client_version}, server={server_version}. "
                    f"Returning 409 to force reload."
                )
                return HttpResponse(
                    status=409,
                    headers={"X-Inertia-Location": request.build_absolute_uri()},
                )

        # Get shared data from middleware
        shared_data = getattr(request, "_inertia_shared", {})

        # Handle partial reloads
        partial_component = request.headers.get("X-Inertia-Partial-Component")  # type: ignore[attr-defined]
        partial_data = request.headers.get("X-Inertia-Partial-Data")  # type: ignore[attr-defined]
        partial_except = request.headers.get("X-Inertia-Partial-Except")  # type: ignore[attr-defined]

        # Parse X-Inertia-Reset header
        reset_header = request.headers.get("X-Inertia-Reset")  # type: ignore[attr-defined]
        reset_props: list[str] = []
        if reset_header:
            reset_props = [
                key.strip() for key in reset_header.split(",") if key.strip()
            ]
            logger.info(f"Reset props requested: {reset_props}")

        # Track special prop types
        optional_prop_keys = {
            key for key, val in props.items() if _is_optional_prop(val)
        }
        always_prop_keys = {key for key, val in props.items() if _is_always_prop(val)}

        # Build deferred props map
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
                requested_keys = [key.strip() for key in partial_data.split(",")]
                filtered_props = {
                    key: props[key] for key in requested_keys if key in props
                }
                always_props = {key: props[key] for key in always_prop_keys}
                props = {**shared_data, **always_props, **filtered_props}
                deferred_props_map = {}
                logger.info(
                    f"Partial reload: requested props {requested_keys} + shared data {list(shared_data.keys())} + always props {list(always_prop_keys)} for {component}"
                )
            elif partial_except:
                except_keys = [key.strip() for key in partial_except.split(",")]
                shared_data_keys = set(shared_data.keys())
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
                props = {**shared_data, **filtered_props}
                logger.info(
                    f"Partial reload: excluding props {except_keys} (preserving shared data and always props) for {component}"
                )
        else:
            # No partial reload - merge all shared data with page props
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
                props = {**shared_data, **props}
                logger.debug(
                    f"Merged shared data keys {list(shared_data.keys())} with page props"
                )

        # Resolve callable props
        props = _resolve_props_sync(props)

        # Add errors to props
        if errors:
            if error_bag := request.headers.get("X-Inertia-Error-Bag"):  # type: ignore[attr-defined]
                props["errors"] = {error_bag: errors}
                logger.info(
                    f"Rendering {component} with validation errors in bag '{error_bag}': {list(errors.keys())}"
                )
            else:
                props["errors"] = errors
                logger.info(
                    f"Rendering {component} with validation errors: {list(errors.keys())}"
                )

        # Build page data
        page_data: dict[str, Any] = {
            "component": component,
            "props": props,
            "url": url_path,
            "version": self.get_asset_version(),
            "encryptHistory": encrypt_history,
            "clearHistory": clear_history,
        }

        # Add merge/prepend props (filter out reset props)
        def should_exclude_from_merge(prop: str) -> bool:
            for reset_prop in reset_props:
                if prop == reset_prop or prop.startswith(f"{reset_prop}."):
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

        if reset_props:
            page_data["resetProps"] = reset_props
            logger.info(f"Including resetProps in response: {reset_props}")

        if deferred_props_map:
            page_data["deferredProps"] = deferred_props_map
            logger.info(f"Deferred props: {deferred_props_map}")

        if self.is_inertia_request(request):
            # Return JSON response for Inertia XHR requests
            is_prefetch = self.is_prefetch_request(request)
            request_type = "Prefetch" if is_prefetch else "Inertia XHR"
            logger.info(f"-> {request_type}: {component} (props: {list(props.keys())})")

            response = JsonResponse(page_data)
            response["X-Inertia"] = "true"
            response["Vary"] = "X-Inertia"
            return response
        else:
            # Return HTML response for initial page load
            logger.info(
                f"-> Initial page load: {component} (props: {list(props.keys())})"
            )

            # Escape single quotes in JSON for safe embedding in HTML attributes
            page_json = json.dumps(page_data).replace("'", "&#39;")

            template_context = {
                "page": page_json,
                "vite_tags": self.get_vite_tags(),
            }

            # Add view_data to template context if provided
            if view_data:
                template_context.update(view_data)
                logger.debug(f"Adding view_data to template: {list(view_data.keys())}")

            return TemplateResponse(request, self.template_name, template_context)
