from typing import TYPE_CHECKING, ClassVar

from django.contrib import admin

from app_account.forms import UserAddressBaseForm
from app_account.models import (
    UserAddressModel,
    UserModel,
)

if TYPE_CHECKING:
    BaseUserAddressInlineAdmin = admin.TabularInline[
        UserAddressModel,
        UserModel,
    ]
else:
    BaseUserAddressInlineAdmin = admin.TabularInline


class UserAddressInlineAdmin(BaseUserAddressInlineAdmin):
    model = UserAddressModel
    form = UserAddressBaseForm
    fk_name = "user"
    extra = 1

    fields = (
        "primary",
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

    class Media:
        css: ClassVar[dict[str, tuple[str, ...]]] = {
            "all": ("src/css/admin/user_address_inline.css",),
        }
        js = ("src/js/admin/user_address_inline.js",)
