from typing import TYPE_CHECKING

from django import forms

from address.models import CityModel

from .mixins import NormalizedAddressNameFieldMixin

if TYPE_CHECKING:
    BaseCityForm = forms.ModelForm[CityModel]
else:
    BaseCityForm = forms.ModelForm


class CityForm(
    NormalizedAddressNameFieldMixin,
    BaseCityForm,
):
    class Meta:
        model = CityModel
        fields = (
            "name",
            "state",
        )
