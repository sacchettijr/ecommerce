from typing import Any, cast

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from account.models import UserModel


class LoginForm(AuthenticationForm):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.error_messages = {
            **self.error_messages,
            "inactive": _(
                message="This account has been deactivated.",
            ),
            "email_not_verified": _(
                message=(
                    "You haven't confirmed your email yet. "
                    "Check your inbox to activate the account."
                ),
            ),
        }

        self.unverified_user: UserModel | None = None

    def __get_login_error(
        self,
        username: str,
        password: str,
    ) -> forms.ValidationError:
        try:
            user = UserModel.objects.get_by_natural_key(
                username=username,
            )
        except UserModel.DoesNotExist:
            return self.get_invalid_login_error()

        if not user.check_password(
            raw_password=password,
        ):
            return self.get_invalid_login_error()

        if not user.is_active:
            return forms.ValidationError(
                message=self.error_messages["inactive"],
                code="inactive",
            )

        is_email_verified = cast(
            bool,
            user.is_email_verified,
        )

        if not is_email_verified:
            self.unverified_user = user

            return forms.ValidationError(
                message=self.error_messages["email_not_verified"],
                code="email_not_verified",
            )

        return self.get_invalid_login_error()

    @sensitive_variables()
    def clean(self) -> dict[str, Any]:
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                request=self.request,
                username=username,
                password=password,
            )

        if self.user_cache is None:
            if not isinstance(username, str) or not isinstance(
                password,
                str,
            ):
                raise self.get_invalid_login_error()

            raise self.__get_login_error(
                username,
                password,
            )

        self.confirm_login_allowed(
            user=self.user_cache,
        )

        return self.cleaned_data
