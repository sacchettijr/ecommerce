from typing import Any

from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.normalize import normalize_whitespace
from utils.validator import validate_name


class NormalizedNameFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_name(self) -> str:
        name = normalize_whitespace(
            name=self.cleaned_data["name"],
        )

        if len(name) < 3:
            raise forms.ValidationError(
                message=_(
                    message="The name must be 3 characters.",
                ),
            )

        #   Shared with the contact form (utils/validator.py) — also requires a first and
        #   a last name, not just one word.
        validate_name(
            value=name,
        )

        return name
