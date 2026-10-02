from typing import (
    cast,
)

from django.contrib.auth.base_user import (
    AbstractBaseUser,
)
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
)

from account.models import (
    UserModel,
)


class EmailVerificationTokenGenerator(
    PasswordResetTokenGenerator,
):
    def _make_hash_value(
        self,
        user: AbstractBaseUser,
        timestamp: int,
    ) -> str:
        user_model = cast(
            UserModel,
            user,
        )

        user_pk = cast(
            int,
            user_model.pk,
        )
        user_email = cast(
            str,
            user_model.email,
        )
        user_is_email_verified = cast(
            bool,
            user_model.is_email_verified,
        )

        return f"{user_pk}{user_email}{user_is_email_verified}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
