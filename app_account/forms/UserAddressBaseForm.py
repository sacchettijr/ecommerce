from typing import TYPE_CHECKING, Any

from django import forms
from django.core.exceptions import ValidationError
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
from app_address.forms.widgets import CityLocationSelect, StateLocationSelect
from app_address.models import CityModel, StateModel

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
    #   django-stubs declares error_messages as an instance attribute on Form, so it can't be
    #   annotated ClassVar here without conflicting with that base class typing.
    error_messages = {  # noqa: RUF012
        "state_country_mismatch": _(
            message="This state does not belong to the selected country.",
        ),
        "city_state_mismatch": _(
            message="This city does not belong to the selected state.",
        ),
    }

    state = forms.ModelChoiceField(
        queryset=StateModel.objects.select_related("country"),
        label=_(message="State/Province"),
        widget=StateLocationSelect,
    )
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
            "country",
            "state",
            "city",
        )

    def clean(self) -> dict[str, Any]:
        super().clean()
        country = self.cleaned_data.get("country")
        state = self.cleaned_data.get("state")
        city = self.cleaned_data.get("city")

        #   JS keeps the dropdowns in sync client-side, but the server never trusts that: a
        #   manually-crafted or stale submission must still be rejected here.
        if state and country and state.country_id != country.id:
            self.add_error(
                "state",
                ValidationError(
                    self.error_messages["state_country_mismatch"],
                    code="state_country_mismatch",
                ),
            )

        if city and state and city.state_id != state.id:
            self.add_error(
                "city",
                ValidationError(
                    self.error_messages["city_state_mismatch"],
                    code="city_state_mismatch",
                ),
            )

        return self.cleaned_data
