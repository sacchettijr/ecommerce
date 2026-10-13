from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import RegionalPhoneNumberWidget


class PhoneFieldMixin(forms.Form):
    phone = PhoneNumberField(
        label=_(
            message="Phone",
        ),
        required=False,
        widget=RegionalPhoneNumberWidget(
            attrs={
                "autocomplete": "tel",
                "placeholder": "(11) 98765-4321",
            },
        ),
    )
