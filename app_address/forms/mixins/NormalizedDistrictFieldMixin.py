from typing import (
    Any,
)

from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.normalize import normalize_whitespace


class NormalizedDistrictFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_district(self) -> str:
        district = normalize_whitespace(
            name=self.cleaned_data["district"],
        )
        if len(district) < 3:
            raise forms.ValidationError(
                message=_(
                    message="The district must have at least 3 characters.",
                ),
            )
        return district
