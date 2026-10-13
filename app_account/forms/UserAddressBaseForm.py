from typing import TYPE_CHECKING

from django import forms
from django.utils.translation import (
    gettext_lazy as _,
)

from app_account.models import UserAddressModel
from app_address.forms.mixins import (
    NormalizedComplementFieldMixin,
    NormalizedDistrictFieldMixin,
    NormalizedNumberFieldMixin,
    NormalizedPostalCodeFieldMixin,
    NormalizedReferenceFieldMixin,
    NormalizedStreetFieldMixin,
)
from app_address.forms.widgets import CityLocationSelect
from app_address.models import CityModel

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
    city = forms.ModelChoiceField(
        queryset=CityModel.objects.select_related("state__country"),
        label=_(message="City"),
        widget=CityLocationSelect,
    )

    class Meta:
        model = UserAddressModel
        fields = (
            "primary",
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
        )
