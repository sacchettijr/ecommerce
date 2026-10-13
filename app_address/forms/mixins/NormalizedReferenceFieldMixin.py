from typing import (
    Any,
)

from utils.normalize import normalize_whitespace


class NormalizedReferenceFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_reference(self) -> str:
        reference = self.cleaned_data.get("reference") or ""
        return normalize_whitespace(
            name=reference,
        )
