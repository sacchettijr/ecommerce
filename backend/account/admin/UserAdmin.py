from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from django.utils.translation import (
    gettext_lazy as _,
)

from account.forms import (
    UserAdminChangeForm,
    UserAdminCreationForm,
)
from account.models import UserModel

if TYPE_CHECKING:
    UserAdminBase = BaseUserAdmin[UserModel]
else:
    UserAdminBase = BaseUserAdmin


@admin.register(UserModel)
class UserAdmin(UserAdminBase):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            _(message="Personal information"),
            {
                "fields": (
                    "name",
                    "date_birth",
                    "phone",
                ),
            },
        ),
        (
            _(message="Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _(message="Important dates"),
            {
                "fields": ("last_login",),
            },
        ),
        (
            _(message="Audit"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "email",
                    "date_birth",
                    "phone",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "last_login",
    )

    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "date_birth",
        "is_active",
        "is_staff",
        "is_email_verified",
        "is_superuser",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "date_birth",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_email_verified",
        "created_at",
    )

    ordering = ("email",)

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
