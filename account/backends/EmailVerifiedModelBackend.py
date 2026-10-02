from typing import cast

from django.contrib.auth.backends import ModelBackend

from account.models import UserModel


class EmailVerifiedModelBackend(
    ModelBackend,
):
    def user_can_authenticate(
        self,
        user: object | None,
    ) -> bool:
        if not isinstance(user, UserModel):
            return False

        #   Cast created to solve the problem of 'user.is_email_verified' unknown on basedpyright.
        return user.is_active and cast(
            bool,
            user.is_email_verified,
        )
