from typing import TYPE_CHECKING

from django import forms

from address.models import StateModel

from .mixins import NormalizedAddressNameFieldMixin

if TYPE_CHECKING:
    BaseStateForm = forms.ModelForm[StateModel]
else:
    BaseStateForm = forms.ModelForm


class StateForm(
    NormalizedAddressNameFieldMixin,
    BaseStateForm,
):
    class Meta:
        model = StateModel
        fields = (
            "name",
            "code",
            "country",
        )
