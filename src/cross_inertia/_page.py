"""Shared Inertia page builder used by framework adapters."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse

from ._props import always, defer, once, optional
from ._utils import _resolve_props_sync

_SPECIAL_PROP_TYPES = (optional, always, defer, once)


class PageRequestAdapter(Protocol):
    """Minimal adapter interface needed to normalize an Inertia request."""

    @property
    def method(self) -> str: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def url(self) -> str: ...


@dataclass(slots=True)
class PageRequestContext:
    """Normalized request facts needed to build an Inertia page."""

    method: str
    headers: Mapping[str, str]
    current_url: str
    page_url: str
    shared_data: dict[str, Any]
    asset_version: str
    is_inertia: bool
    is_prefetch: bool
    partial_component: str | None
    partial_only: list[str]
    partial_except: list[str]
    reset_props: list[str]
    except_once_props: set[str]
    error_bag: str | None
    version_conflict_location: str


@dataclass(slots=True)
class PageRenderOptions:
    """Normalized render inputs shared by framework adapters."""

    component: str
    props: dict[str, Any]
    errors: dict[str, str] | None = None
    encrypt_history: bool = False
    clear_history: bool = False
    merge_props: list[str] | None = None
    prepend_props: list[str] | None = None
    deep_merge_props: list[str] | None = None
    match_props_on: list[str] | None = None
    scroll_props: dict[str, Any] | None = None


@dataclass(slots=True)
class PageBuildResult:
    """Result of building an Inertia page."""

    is_inertia: bool
    is_prefetch: bool
    page_data: dict[str, Any] | None = None
    page_json: str | None = None
    version_conflict_location: str | None = None


@dataclass(slots=True)
class _PropTraits:
    optional: optional | None = None
    always: always | None = None
    deferred: defer | None = None
    once: once | None = None


@dataclass(slots=True)
class _CollectedMetadata:
    deferred_props: dict[str, list[str]] = field(default_factory=dict)
    once_props: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_deferred(self, group: str, path: str) -> None:
        group_props = self.deferred_props.setdefault(group, [])
        if path not in group_props:
            group_props.append(path)

    def add_once(self, once_key: str, prop_path: str, expires_at: int | None) -> None:
        self.once_props[once_key] = {
            "prop": prop_path,
            "expiresAt": expires_at,
        }


def parse_header_list(value: str | None) -> list[str]:
    """Parse a comma-separated request header into a list of prop paths."""
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def is_inertia_request_headers(headers: Mapping[str, str]) -> bool:
    """Check if headers represent an Inertia XHR request."""
    return headers.get("X-Inertia") == "true"


def is_prefetch_request_headers(headers: Mapping[str, str]) -> bool:
    """Check if headers represent an Inertia prefetch request."""
    return is_inertia_request_headers(headers) and headers.get("Purpose") == "prefetch"


def build_page_request_context(
    *,
    adapter: PageRequestAdapter,
    shared_data: Mapping[str, Any] | None,
    asset_version: str,
    url: str | None = None,
    version_conflict_location: str | None = None,
) -> PageRequestContext:
    """Build shared request context from a normalized framework adapter."""
    headers = adapter.headers
    current_url = adapter.url

    return PageRequestContext(
        method=adapter.method,
        headers=headers,
        current_url=current_url,
        page_url=_resolve_page_url(current_url, url),
        shared_data=dict(shared_data or {}),
        asset_version=asset_version,
        is_inertia=is_inertia_request_headers(headers),
        is_prefetch=is_prefetch_request_headers(headers),
        partial_component=headers.get("X-Inertia-Partial-Component"),
        partial_only=parse_header_list(headers.get("X-Inertia-Partial-Data")),
        partial_except=parse_header_list(headers.get("X-Inertia-Partial-Except")),
        reset_props=parse_header_list(headers.get("X-Inertia-Reset")),
        except_once_props=set(
            parse_header_list(headers.get("X-Inertia-Except-Once-Props"))
        ),
        error_bag=headers.get("X-Inertia-Error-Bag"),
        version_conflict_location=version_conflict_location or current_url,
    )


def build_inertia_page(
    context: PageRequestContext,
    options: PageRenderOptions,
) -> PageBuildResult:
    """Build the canonical Inertia page object for any framework adapter."""
    is_partial = (
        context.is_inertia
        and context.partial_component == options.component
        and bool(context.partial_only or context.partial_except)
    )

    if _has_version_conflict(context):
        return PageBuildResult(
            is_inertia=context.is_inertia,
            is_prefetch=context.is_prefetch,
            version_conflict_location=context.version_conflict_location,
        )

    merged_props = {**context.shared_data, **options.props}
    metadata = _CollectedMetadata()
    filtered_props: dict[str, Any] = {}

    for key, value in merged_props.items():
        include, filtered_value = _walk_node(
            value=value,
            path=key,
            context=context,
            is_partial=is_partial,
            metadata=metadata,
        )
        if include:
            filtered_props[key] = filtered_value

    resolved_props = _resolve_props_sync(filtered_props)

    if options.errors:
        if context.error_bag:
            resolved_props["errors"] = {context.error_bag: options.errors}
        else:
            resolved_props["errors"] = options.errors

    page_data: dict[str, Any] = {
        "component": options.component,
        "props": resolved_props,
        "url": context.page_url,
        "version": context.asset_version,
        "encryptHistory": options.encrypt_history,
        "clearHistory": options.clear_history,
    }

    filtered_merge = _filter_merge_metadata(
        options.merge_props,
        reset_props=context.reset_props,
        partial_only=context.partial_only if is_partial else [],
        partial_except=context.partial_except if is_partial else [],
    )
    filtered_prepend = _filter_merge_metadata(
        options.prepend_props,
        reset_props=context.reset_props,
        partial_only=context.partial_only if is_partial else [],
        partial_except=context.partial_except if is_partial else [],
    )
    filtered_deep = _filter_merge_metadata(
        options.deep_merge_props,
        reset_props=context.reset_props,
        partial_only=context.partial_only if is_partial else [],
        partial_except=context.partial_except if is_partial else [],
    )
    filtered_match = _filter_match_metadata(
        options.match_props_on,
        reset_props=context.reset_props,
    )

    if filtered_merge:
        page_data["mergeProps"] = filtered_merge
    if filtered_prepend:
        page_data["prependProps"] = filtered_prepend
    if filtered_deep:
        page_data["deepMergeProps"] = filtered_deep
    if filtered_match:
        page_data["matchPropsOn"] = filtered_match
    if options.scroll_props:
        page_data["scrollProps"] = options.scroll_props
    if context.reset_props:
        page_data["resetProps"] = context.reset_props
    if metadata.deferred_props:
        page_data["deferredProps"] = metadata.deferred_props
    if metadata.once_props:
        page_data["onceProps"] = metadata.once_props

    return PageBuildResult(
        is_inertia=context.is_inertia,
        is_prefetch=context.is_prefetch,
        page_data=page_data,
        page_json=json.dumps(page_data).replace("'", "&#39;"),
    )


def _resolve_page_url(current_url: str, override_url: str | None) -> str:
    if override_url is not None:
        return override_url

    parsed_url = urlparse(current_url)
    if parsed_url.query:
        return f"{parsed_url.path}?{parsed_url.query}"

    return parsed_url.path


def _walk_node(
    *,
    value: Any,
    path: str,
    context: PageRequestContext,
    is_partial: bool,
    metadata: _CollectedMetadata,
) -> tuple[bool, Any]:
    traits = _collect_prop_traits(value)

    if traits.once and _should_emit_once_metadata(path, traits, context, is_partial):
        metadata.add_once(
            traits.once.key or path,
            path,
            traits.once.expires_at(),
        )

    if traits.deferred and _should_emit_deferred_metadata(
        path, traits, context, is_partial
    ):
        metadata.add_deferred(traits.deferred.group, path)

    if isinstance(value, _SPECIAL_PROP_TYPES):
        if _should_include_special_prop(path, traits, context, is_partial):
            return True, value
        return False, None

    if isinstance(value, dict):
        filtered: dict[str, Any] = {}
        for key, child_value in value.items():
            child_path = f"{path}.{key}"
            include, filtered_value = _walk_node(
                value=child_value,
                path=child_path,
                context=context,
                is_partial=is_partial,
                metadata=metadata,
            )
            if include:
                filtered[key] = filtered_value

        if filtered or _should_include_container(path, context, is_partial):
            return True, filtered
        return False, None

    if isinstance(value, list):
        filtered_items: list[Any] = []
        for index, child_value in enumerate(value):
            child_path = f"{path}.{index}"
            include, filtered_value = _walk_node(
                value=child_value,
                path=child_path,
                context=context,
                is_partial=is_partial,
                metadata=metadata,
            )
            if include:
                filtered_items.append(filtered_value)

        if filtered_items or _should_include_container(path, context, is_partial):
            return True, filtered_items
        return False, None

    if _should_include_container(path, context, is_partial):
        return True, value
    return False, None


def _collect_prop_traits(value: Any) -> _PropTraits:
    traits = _PropTraits()
    current = value
    visited: set[int] = set()

    while isinstance(current, _SPECIAL_PROP_TYPES):
        current_id = id(current)
        if current_id in visited:
            break
        visited.add(current_id)

        if isinstance(current, once) and traits.once is None:
            traits.once = current
        elif isinstance(current, defer) and traits.deferred is None:
            traits.deferred = current
        elif isinstance(current, optional) and traits.optional is None:
            traits.optional = current
        elif isinstance(current, always) and traits.always is None:
            traits.always = current

        nested = _extract_nested_special_prop(current)
        if nested is None:
            break
        current = nested

    return traits


def _extract_nested_special_prop(value: Any) -> Any | None:
    if isinstance(value, once):
        nested = value.value_or_callback
        return nested if isinstance(nested, _SPECIAL_PROP_TYPES) else None

    if isinstance(value, always):
        if value.args or value.kwargs:
            return None
        nested = value.value_or_callback
        return nested if isinstance(nested, _SPECIAL_PROP_TYPES) else None

    if isinstance(value, (optional, defer)):
        if value.args or value.kwargs:
            return None
        nested = value.callback
        return nested if isinstance(nested, _SPECIAL_PROP_TYPES) else None

    return None


def _should_include_special_prop(
    path: str,
    traits: _PropTraits,
    context: PageRequestContext,
    is_partial: bool,
) -> bool:
    if traits.always is not None:
        return True

    if is_partial:
        if not _path_allowed_for_partial(
            path, context.partial_only, context.partial_except
        ):
            return False

        if traits.optional is not None or traits.deferred is not None:
            return _path_explicitly_requested(path, context.partial_only)

        return True

    if traits.optional is not None or traits.deferred is not None:
        return False

    return not _should_skip_once_value(path, traits, context, is_partial)


def _should_include_container(
    path: str,
    context: PageRequestContext,
    is_partial: bool,
) -> bool:
    if not is_partial:
        return True

    return _path_allowed_for_partial(path, context.partial_only, context.partial_except)


def _should_emit_deferred_metadata(
    path: str,
    traits: _PropTraits,
    context: PageRequestContext,
    is_partial: bool,
) -> bool:
    if traits.deferred is None or is_partial:
        return False

    return not _should_skip_once_value(path, traits, context, is_partial)


def _should_emit_once_metadata(
    path: str,
    traits: _PropTraits,
    context: PageRequestContext,
    is_partial: bool,
) -> bool:
    if traits.once is None:
        return False

    if not is_partial:
        return True

    if traits.always is not None:
        return True

    return _path_allowed_for_partial(path, context.partial_only, context.partial_except)


def _should_skip_once_value(
    path: str,
    traits: _PropTraits,
    context: PageRequestContext,
    is_partial: bool,
) -> bool:
    if is_partial or not context.is_inertia or traits.once is None:
        return False

    if traits.once.fresh:
        return False

    return (traits.once.key or path) in context.except_once_props


def _path_allowed_for_partial(
    path: str,
    partial_only: list[str],
    partial_except: list[str],
) -> bool:
    if partial_only and not _path_explicitly_requested(path, partial_only):
        return False

    if _path_excluded(path, partial_except):
        return False

    return True


def _path_explicitly_requested(path: str, selectors: list[str]) -> bool:
    return any(_paths_overlap(path, selector) for selector in selectors)


def _path_excluded(path: str, selectors: list[str]) -> bool:
    return any(
        path == selector or path.startswith(f"{selector}.") for selector in selectors
    )


def _paths_overlap(path: str, selector: str) -> bool:
    return (
        path == selector
        or path.startswith(f"{selector}.")
        or selector.startswith(f"{path}.")
    )


def _has_version_conflict(context: PageRequestContext) -> bool:
    client_version = context.headers.get("X-Inertia-Version")
    return (
        context.is_inertia
        and context.method.upper() == "GET"
        and bool(client_version)
        and client_version != context.asset_version
    )


def _filter_merge_metadata(
    prop_paths: list[str] | None,
    *,
    reset_props: list[str],
    partial_only: list[str],
    partial_except: list[str],
) -> list[str]:
    if not prop_paths:
        return []

    filtered = [
        path
        for path in prop_paths
        if not _path_matches_reset(path, reset_props)
        and _path_allowed_for_partial(path, partial_only, partial_except)
    ]
    return filtered


def _filter_match_metadata(
    prop_paths: list[str] | None,
    *,
    reset_props: list[str],
) -> list[str]:
    if not prop_paths:
        return []

    return [path for path in prop_paths if not _path_matches_reset(path, reset_props)]


def _path_matches_reset(path: str, reset_props: list[str]) -> bool:
    return any(
        path == reset_prop or path.startswith(f"{reset_prop}.")
        for reset_prop in reset_props
    )
