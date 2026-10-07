from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from django import forms
from django.db import transaction

from account.models import (
    UserAddressModel,
    UserModel,
)
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
    class Meta:
        model = UserAddressModel
        fields = (
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

    def __init__(
        self,
        *args: Any,
        user: UserModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def save(
        self,
        commit: bool = True,
    ) -> UserAddressModel:
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            with transaction.atomic():
                if cast(bool, instance.primary):
                    UserAddressModel.objects.filter(
                        user=self.user,
                        primary=True,
                    ).exclude(
                        pk=instance.pk,
                    ).update(
                        primary=False,
                    )

                instance.save()

        return instance
