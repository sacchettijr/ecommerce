from typing import TYPE_CHECKING

from django.contrib.auth.forms import UserCreationForm

from app_account.forms.mixins import (
    NormalizedEmailFieldMixin,
    NormalizedNameFieldMixin,
)
from app_account.models import UserModel

if TYPE_CHECKING:
    ModelFormBase = UserCreationForm[UserModel]
else:
    ModelFormBase = UserCreationForm


class UserAdminCreationForm(
    NormalizedNameFieldMixin,
    NormalizedEmailFieldMixin,
    ModelFormBase,
):
    class Meta:
        model = UserModel
        fields = (
            "name",
            "email",
            "date_birth",
            "phone",
            "is_active",
            "is_staff",
            "is_superuser",
        )
