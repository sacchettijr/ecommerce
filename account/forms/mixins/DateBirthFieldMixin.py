from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)


class DateBirthFieldMixin(forms.Form):
    date_birth = forms.DateField(
        label=_(
            message="Date of birth",
        ),
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "autocomplete": "bday",
            },
            format="%Y-%m-%d",
        ),
    )
