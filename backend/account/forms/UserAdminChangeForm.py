from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Permission
from django.db.models import QuerySet
from django.utils.translation import (
    gettext_lazy as _,
)

from account.forms.mixins import (
    NormalizedEmailFieldMixin,
    NormalizedNameFieldMixin,
)
from account.models import UserModel

if TYPE_CHECKING:
    ModelFormBase = forms.ModelForm[UserModel]
else:
    ModelFormBase = forms.ModelForm


class UserAdminChangeForm(
    NormalizedNameFieldMixin,
    NormalizedEmailFieldMixin,
    ModelFormBase,
):
    password = ReadOnlyPasswordHashField(
        label=_(
            message="Password",
        ),
        help_text=_(
            message=(
                "Passwords are not stored in plain text, so it is not "
                "possible to see this user's password, but you can change "
                'it using <a href="{}">this form</a>.'
            ),
        ),
    )

    class Meta:
        model = UserModel
        fields = (
            "name",
            "email",
            "date_birth",
            "phone",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_email_verified",
            "groups",
            "user_permissions",
        )

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        password = self.fields.get("password")

        if password:
            password.help_text = password.help_text.format(
                "../password/",
            )

        user_permissions = self.fields.get("user_permissions")

        if isinstance(
            user_permissions,
            forms.ModelMultipleChoiceField,
        ):
            queryset = cast(
                QuerySet[Permission, Permission] | None,
                user_permissions.queryset,
            )

            if queryset is not None:
                user_permissions.queryset = queryset.select_related(
                    "content_type",
                )
