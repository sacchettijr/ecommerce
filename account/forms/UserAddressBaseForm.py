from typing import TYPE_CHECKING

from django import forms

from account.models import UserAddressModel
from address.forms.mixins import (
    NormalizedComplementFieldMixin,
    NormalizedDistrictFieldMixin,
    NormalizedNumberFieldMixin,
    NormalizedPostalCodeFieldMixin,
    NormalizedReferenceFieldMixin,
    NormalizedStreetFieldMixin,
)

if TYPE_CHECKING:
    BaseUserAddressForm = forms.ModelForm[UserAddressModel]
else:
    BaseUserAddressForm = forms.ModelForm


class UserAddressBaseForm(
    NormalizedStreetFieldMixin,
    NormalizedNumberFieldMixin,
    NormalizedComplementFieldMixin,
    NormalizedReferenceFieldMixin,
    NormalizedDistrictFieldMixin,
    NormalizedPostalCodeFieldMixin,
    BaseUserAddressForm,
):
    #   "user" fica no Meta.fields para o admin autônomo (UserAddressAdmin, que lista
    #   endereços de todos os usuários). No inline sob UserAdmin, o próprio formset do
    #   Django preenche "user" automaticamente a partir do objeto pai — o inline
    #   controla o que aparece de fato através do próprio "fields" dele.
    class Meta:
        model = UserAddressModel
        fields = (
            "user",
            "street",
            "number",
            "complement",
            "reference",
            "district",
            "postal_code",
            "city",
            "state",
            "country",
            "primary",
        )
