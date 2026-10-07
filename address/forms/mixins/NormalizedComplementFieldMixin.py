from typing import (
    Any,
)

from utils.normalize import normalize_whitespace


class NormalizedComplementFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_complement(self) -> str:
        complement = self.cleaned_data.get("complement") or ""
        return normalize_whitespace(
            name=complement,
        )
