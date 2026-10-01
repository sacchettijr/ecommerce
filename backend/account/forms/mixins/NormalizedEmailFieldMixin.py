from typing import Any

from utils.normalize import normalize_email


class NormalizedEmailFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_email(self) -> str:

        return normalize_email(
            email=self.cleaned_data["email"],
        )
