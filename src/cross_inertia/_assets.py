from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


def normalize_entry_key(entry: str) -> str:
    """Normalize a Vite manifest entry key for matching."""
    return entry.replace("\\", "/").lstrip("./")


def resolve_manifest_entry(
    manifest: dict[str, Any],
    configured_entry: str,
) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve a manifest entry, with fallbacks for common Vite output shapes."""
    if configured_entry in manifest and isinstance(manifest[configured_entry], dict):
        return configured_entry, manifest[configured_entry]

    normalized_entry = normalize_entry_key(configured_entry)
    entry_candidates = [
        (key, value)
        for key, value in manifest.items()
        if isinstance(value, dict) and "file" in value
    ]

    for key, value in entry_candidates:
        if normalize_entry_key(key) == normalized_entry:
            return key, value

    configured_name = PurePosixPath(normalized_entry).name
    basename_matches = [
        (key, value)
        for key, value in entry_candidates
        if PurePosixPath(normalize_entry_key(key)).name == configured_name
    ]
    if len(basename_matches) == 1:
        return basename_matches[0]

    explicit_entries = [
        (key, value)
        for key, value in entry_candidates
        if value.get("isEntry") is True
    ]
    if len(explicit_entries) == 1:
        return explicit_entries[0]

    if len(entry_candidates) == 1:
        return entry_candidates[0]

    return None, None


def build_asset_url(asset_url_prefix: str, relative_path: str) -> str:
    """Build a public asset URL from a configured prefix and a manifest path."""
    prefix = asset_url_prefix.rstrip("/")
    path = relative_path.lstrip("/")
    return f"{prefix}/{path}"
