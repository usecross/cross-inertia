from __future__ import annotations

from typing import TypeAlias

ValidationErrorValue: TypeAlias = str | list[str]
ValidationErrors: TypeAlias = dict[str, "ValidationErrorValue | ValidationErrors"]
