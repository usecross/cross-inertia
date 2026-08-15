"""Django-specific Inertia response handling."""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import hashlib
import logging
import warnings
from pathlib import Path
from typing import Any

import httpx
from cross_web import DjangoHTTPRequestAdapter

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse

from .._assets import (
    build_asset_url,
    build_vite_dev_url,
    normalize_vite_base,
    resolve_manifest_entry,
)
from .._exceptions import ManifestNotFoundError
from .._ssr import VITE_DEV_SSR_ENDPOINT, InertiaSSR
from .conf import inertia_settings
from .._page import (
    PageRenderOptions,
    build_page_request_context,
    build_inertia_page,
    is_inertia_request_headers,
    is_prefetch_request_headers,
)
from .._types import ValidationErrors

logger = logging.getLogger(__name__)

_VITE_TAGS_DEPRECATION = (
    "The 'vite_tags' template variable is deprecated. "
    "Use {% inertia_head %} and {% inertia_body %} template tags instead."
)


class _DeprecatedViteTags(str):
    """String subclass that emits a deprecation warning when rendered."""

    _warned = False

    def __str__(self) -> str:
        if not _DeprecatedViteTags._warned:
            _DeprecatedViteTags._warned = True
            warnings.warn(_VITE_TAGS_DEPRECATION, DeprecationWarning, stacklevel=2)
        return super().__str__()


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
        *,
        vite_react_refresh: bool | None = None,
        vite_base: str | None = None,
    ):
        self.template_name = template_name or inertia_settings.LAYOUT
        self.vite_dev_url = vite_dev_url or inertia_settings.VITE_DEV_URL
        self.vite_base = normalize_vite_base(
            vite_base if vite_base is not None else inertia_settings.VITE_BASE
        )
        self.manifest_path = manifest_path or inertia_settings.MANIFEST_PATH
        self.asset_url_prefix = inertia_settings.ASSET_URL_PREFIX
        self.vite_entry = vite_entry or inertia_settings.VITE_ENTRY
        self.vite_react_refresh = (
            vite_react_refresh
            if vite_react_refresh is not None
            else inertia_settings.VITE_REACT_REFRESH
        )
        self.ssr_enabled = (
            ssr_enabled if ssr_enabled is not None else inertia_settings.SSR_ENABLED
        )
        self.ssr_url = ssr_url or inertia_settings.SSR_URL

        self._is_dev: bool | None = None
        self._manifest: dict[str, Any] | None = None
        self._ssr_client: InertiaSSR | None = None
        self._vite_dev_ssr_client: InertiaSSR | None = None
        if self.ssr_enabled:
            self._ssr_client = InertiaSSR(url=self.ssr_url, enabled=True)

    def is_inertia_request(self, request: "HttpRequest") -> bool:
        """Check if request is an Inertia XHR request."""
        return is_inertia_request_headers(request.headers)  # type: ignore[arg-type]

    def is_prefetch_request(self, request: "HttpRequest") -> bool:
        """Check if request is an Inertia prefetch request."""
        return is_prefetch_request_headers(request.headers)  # type: ignore[arg-type]

    def vite_dev_asset_url(self, path: str) -> str:
        """Build a URL served by the Vite dev server, honouring its ``base``."""
        return build_vite_dev_url(self.vite_dev_url, self.vite_base, path)

    def is_dev_mode(self) -> bool:
        """Check if Vite dev server is running."""
        if self._is_dev is not None:
            return self._is_dev

        probe_url = self.vite_dev_asset_url("@vite/client")
        logger.info(f"Checking Vite dev server at {probe_url}...")
        try:
            response = httpx.get(probe_url, timeout=0.1)
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

    def get_ssr_client(self) -> InertiaSSR | None:
        """Return the appropriate SSR client for the current runtime mode."""
        if not self.ssr_enabled:
            return None

        if self.is_dev_mode():
            if self._vite_dev_ssr_client is not None:
                return self._vite_dev_ssr_client

            self._vite_dev_ssr_client = InertiaSSR(
                url=self.vite_dev_url,
                enabled=True,
                render_path=VITE_DEV_SSR_ENDPOINT,
                health_path=VITE_DEV_SSR_ENDPOINT,
            )
            return self._vite_dev_ssr_client

        return self._ssr_client

    def get_vite_tags(self) -> str:
        """Generate script tags for Vite assets."""
        if self.is_dev_mode():
            logger.info(
                f"Generating DEV mode script tags (Vite server: {self.vite_dev_url})"
            )
            vite_client_url = self.vite_dev_asset_url("@vite/client")
            entry_url = self.vite_dev_asset_url(self.vite_entry)
            react_refresh_url = self.vite_dev_asset_url("@react-refresh")
            react_refresh = ""
            if self.vite_react_refresh:
                react_refresh = f"""
                <script type="module">
                    import RefreshRuntime from "{react_refresh_url}"
                    RefreshRuntime.injectIntoGlobalHook(window)
                    window.$RefreshReg$ = () => {{}}
                    window.$RefreshSig$ = () => (type) => type
                    window.__vite_plugin_react_preamble_installed__ = true
                </script>
                """

            return f"""
                {react_refresh}
                <script type="module" src="{vite_client_url}"></script>
                <script type="module" src="{entry_url}"></script>
            """
        else:
            manifest = self.get_manifest()
            resolved_key, entry = resolve_manifest_entry(manifest, self.vite_entry)

            if not entry:
                logger.error(
                    f"No entry found for '{self.vite_entry}' in manifest - did you run 'npm run build'?"
                )
                return ""

            tags = []

            css_files = entry.get("css", [])
            if css_files:
                logger.info(
                    f"Generating PRODUCTION script tags - {len(css_files)} CSS file(s), entry: {resolved_key or entry.get('file', 'none')}"
                )
            for css in css_files:
                tags.append(
                    f'<link rel="stylesheet" href="{build_asset_url(self.asset_url_prefix, css)}">'
                )

            if "file" in entry:
                tags.append(
                    f'<script type="module" src="{build_asset_url(self.asset_url_prefix, entry["file"])}"></script>'
                )
            else:
                logger.warning("No JS entry file found in manifest!")

            return "\n".join(tags)

    def render(
        self,
        request: "HttpRequest",
        component: str,
        props: dict[str, Any],
        errors: ValidationErrors | None = None,
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
        schema: Any | None = None,
        status_code: int = 200,
    ) -> HttpResponse:
        """Render an Inertia response for Django."""
        adapter = DjangoHTTPRequestAdapter(request)

        build_result = build_inertia_page(
            build_page_request_context(
                adapter=adapter,
                shared_data=getattr(request, "_inertia_shared", {}),
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
                schema=schema,
            ),
        )

        if build_result.version_conflict_location is not None:
            logger.info(
                "Asset version mismatch detected for GET Inertia request. Returning 409 to force reload."
            )
            return HttpResponse(
                status=409,
                headers={
                    "X-Inertia-Location": build_result.version_conflict_location,
                    "Vary": "X-Inertia",
                },
            )

        assert build_result.page_data is not None
        assert build_result.page_json is not None

        if build_result.is_inertia:
            # Return JSON response for Inertia XHR requests
            request_type = "Prefetch" if build_result.is_prefetch else "Inertia XHR"
            logger.info(
                f"-> {request_type}: {component} (props: {list(build_result.page_data['props'].keys())})"
            )

            response = JsonResponse(build_result.page_data, status=status_code)
            response["X-Inertia"] = "true"
            response["Vary"] = "X-Inertia"
            return response
        else:
            # Return HTML response for initial page load
            logger.info(
                f"-> Initial page load: {component} (props: {list(build_result.page_data['props'].keys())})"
            )

            ssr_head: list[str] = []
            ssr_body: str = ""
            ssr_client = self.get_ssr_client()
            if ssr_client:
                try:
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None

                    if loop is not None:
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run,
                                ssr_client.render(build_result.page_data),
                            )
                            ssr_result = future.result(timeout=5.0)
                    else:
                        ssr_result = asyncio.run(
                            ssr_client.render(build_result.page_data)
                        )

                    if ssr_result:
                        ssr_head = ssr_result.head
                        ssr_body = ssr_result.body
                        logger.info(f"SSR rendered {component} successfully")
                except Exception as e:
                    logger.warning(f"SSR failed, falling back to CSR: {e}")

            template_context = {
                "page": build_result.page_json,
                "vite_tags": _DeprecatedViteTags(self.get_vite_tags()),
                "head": ssr_head,
                "body": ssr_body,
            }

            # Add view_data to template context if provided
            if view_data:
                template_context.update(view_data)
                logger.debug(f"Adding view_data to template: {list(view_data.keys())}")

            response = TemplateResponse(
                request,
                self.template_name,
                template_context,
                status=status_code,
            )
            response["Vary"] = "X-Inertia"
            return response
