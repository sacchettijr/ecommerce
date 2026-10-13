from typing import (
    Any,
)

from utils.normalize import normalize_whitespace


class NormalizedPostalCodeFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_postal_code(self) -> str:
        return normalize_whitespace(
            name=self.cleaned_data["postal_code"],
        )
