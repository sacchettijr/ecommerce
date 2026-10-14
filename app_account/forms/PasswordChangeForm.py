from typing import Any

from django.contrib.auth.forms import (
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordChangeForm(DjangoPasswordChangeForm):
    #   django-stubs declares error_messages as an instance attribute on SetPasswordMixin, so
    #   it can't be annotated ClassVar here without conflicting with that base class typing.
    error_messages = {  # noqa: RUF012
        **DjangoPasswordChangeForm.error_messages,
        "password_unchanged": _(
            message="The new password must be different from your current password.",
        ),
    }

    def clean(self) -> dict[str, Any]:
        super().clean()
        old_password = self.cleaned_data.get("old_password")
        new_password1 = self.cleaned_data.get("new_password1")

        #   Only compared once the current password is itself confirmed correct — an incorrect
        #   old_password must keep producing its own field-level error, not this one.
        if old_password and new_password1 and self.user.check_password(new_password1):
            raise ValidationError(
                self.error_messages["password_unchanged"],
                code="password_unchanged",
            )

        return self.cleaned_data
