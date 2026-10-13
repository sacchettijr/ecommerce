from typing import (
    Any,
)

from utils.normalize import normalize_whitespace


class NormalizedNumberFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_number(self) -> str:
        return normalize_whitespace(
            name=self.cleaned_data["number"],
        )
