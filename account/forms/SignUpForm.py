from typing import TYPE_CHECKING

from django.contrib.auth.forms import UserCreationForm

from account.forms.mixins import (
    DateBirthFieldMixin,
    NormalizedEmailFieldMixin,
    NormalizedNameFieldMixin,
    PhoneFieldMixin,
)
from account.models import UserModel

if TYPE_CHECKING:
    ModelFormBase = UserCreationForm[UserModel]
else:
    ModelFormBase = UserCreationForm


class SignUpForm(
    DateBirthFieldMixin,
    PhoneFieldMixin,
    NormalizedEmailFieldMixin,
    NormalizedNameFieldMixin,
    ModelFormBase,
):
    class Meta:
        model = UserModel
        fields = (
            "name",
            "email",
            "date_birth",
            "phone",
        )
