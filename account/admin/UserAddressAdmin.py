from typing import (
    TYPE_CHECKING,
)

from django.contrib import admin

from account.forms import (
    UserAddressCreateForm,
    UserAddressUpdateForm,
)
from account.models import UserAddressModel

if TYPE_CHECKING:
    BaseUserAddressAdmin = admin.ModelAdmin[UserAddressModel]
else:
    BaseUserAddressAdmin = admin.ModelAdmin


@admin.register(UserAddressModel)
class UserAddressAdmin(BaseUserAddressAdmin):
    list_display = (
        "user",
        "street",
        "number",
        "district",
        "postal_code",
        "city",
        "state",
        "country",
        "primary",
    )
    list_filter = (
        "user",
        "city",
        "state",
        "country",
        "primary",
    )
    search_fields = (
        "user__email",
        "user__name",
        "street",
        "district",
        "postal_code",
        "city__name",
        "state__name",
        "country__name",
    )

    add_form = UserAddressCreateForm
    form = UserAddressUpdateForm
