from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)

from account.forms.mixins import NormalizedEmailFieldMixin


class ResendVerificationEmailForm(
    NormalizedEmailFieldMixin,
    forms.Form,
):
    email = forms.EmailField(
        label=_(
            message="E-mail",
        ),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
            },
        ),
    )
