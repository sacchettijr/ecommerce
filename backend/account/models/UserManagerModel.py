from __future__ import (
    annotations,
)

from typing import (
    TYPE_CHECKING,
    Any,
)

from django.contrib.auth.base_user import (
    BaseUserManager,
)
from django.utils.translation import (
    gettext_lazy as _,
)

if TYPE_CHECKING:
    from account.models.UserModel import (
        UserModel,
    )


class UserManagerModel(
    BaseUserManager["UserModel"],
):
    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> UserModel:

        if not email:
            raise ValueError(
                _(
                    message="Email is required.",
                ),
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(
            raw_password=password,
        )

        user.save(
            using=self._db,
        )

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> UserModel:

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                _(
                    message="The superuser must have is_staff=True.",
                ),
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                _(
                    message="The superuser must have is_superuser=True.",
                ),
            )

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )
