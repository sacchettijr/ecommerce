from typing import TYPE_CHECKING

from django import forms

from account.forms.mixins import (
    DateBirthFieldMixin,
    NormalizedNameFieldMixin,
    PhoneFieldMixin,
)
from account.models import UserModel

if TYPE_CHECKING:
    ModelFormBase = forms.ModelForm[UserModel]
else:
    ModelFormBase = forms.ModelForm


class UserUpdateForm(
    DateBirthFieldMixin,
    PhoneFieldMixin,
    NormalizedNameFieldMixin,
    ModelFormBase,
):
    class Meta:
        model: UserModel
        fields = (
            "name",
            "date_birth",
            "phone",
        )
