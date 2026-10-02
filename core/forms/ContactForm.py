from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)
from phonenumber_field.formfields import PhoneNumberField

from utils.normalize import (
    normalize_email,
    normalize_whitespace,
)
from utils.validator import (
    validate_name,
)


class ContactForm(
    forms.Form,
):
    name = forms.CharField(
        label=_(
            message="Name",
        ),
        min_length=3,
        max_length=255,
        strip=True,
        validators=[
            validate_name,
        ],
    )

    email = forms.EmailField(
        label=_(
            message="E-Mail",
        )
    )

    phone = PhoneNumberField(
        label=_(
            message="Phone",
        ),
        region="BR",
    )

    message = forms.CharField(
        label=_(
            message="Message",
        ),
        min_length=10,
        max_length=2000,
        strip=True,
    )

    def clean_name(
        self,
    ) -> str:
        name: str = normalize_whitespace(
            name=self.cleaned_data["name"],
        )

        return name

    def clean_email(
        self,
    ) -> str:

        return normalize_email(
            email=self.cleaned_data["email"],
        )

    def clean_message(
        self,
    ) -> str:
        return " ".join(
            self.cleaned_data["message"].split(),
        )
