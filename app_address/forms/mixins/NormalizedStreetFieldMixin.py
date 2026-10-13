from typing import (
    Any,
)

from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.normalize import normalize_whitespace


class NormalizedStreetFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_street(self) -> str:
        street = normalize_whitespace(
            name=self.cleaned_data["street"],
        )
        if len(street) < 3:
            raise forms.ValidationError(
                message=_(
                    message="The street must have at least 3 characters.",
                ),
            )
        return street
