"""Helpers for extracting Inertia page data from rendered HTML."""

from __future__ import annotations

import json
import re
from typing import Any

_PAGE_SCRIPT_RE = re.compile(
    r"<script(?=[^>]*\bdata-page=(?P<quote>[\"'])(?P<app_id>.*?)(?P=quote))"
    r"(?=[^>]*\btype=(?P<type_quote>[\"'])application/json(?P=type_quote))"
    r"[^>]*>(?P<page_json>.*?)</script>",
    re.DOTALL,
)


def extract_page_data(html: str, *, app_id: str = "app") -> dict[str, Any]:
    """Extract the serialized Inertia page object from an HTML response."""
    for match in _PAGE_SCRIPT_RE.finditer(html):
        if match.group("app_id") == app_id:
            return json.loads(match.group("page_json"))

    raise AssertionError(f"Could not find page data script for app id {app_id!r}")
