from typing import TYPE_CHECKING

from django import forms

from address.models import CountryModel

from .mixins import NormalizedAddressNameFieldMixin

if TYPE_CHECKING:
    BaseCountryForm = forms.ModelForm[CountryModel]
else:
    BaseCountryForm = forms.ModelForm


class CountryForm(
    NormalizedAddressNameFieldMixin,
    BaseCountryForm,
):
    class Meta:
        model = CountryModel
        fields = (
            "name",
            "iso_code",
        )
