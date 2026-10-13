from typing import (
    Any,
    ClassVar,
    cast,
)

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import (
    BaseModel,
)
from utils.normalize import (
    normalize_email,
    normalize_whitespace,
)

from .UserManagerModel import (
    UserManagerModel,
)


class UserModel(
    BaseModel,
    AbstractBaseUser,
    PermissionsMixin,
):
    # =========================================================
    #   PERSONAL DATA
    # =========================================================

    name = models.CharField(
        verbose_name=_(
            message="name",
        ),
        max_length=250,
    )
    email = models.EmailField(
        verbose_name=_(
            message="E-mail",
        ),
        unique=True,
        db_index=True,
        max_length=250,
    )
    date_birth = models.DateField(
        verbose_name=_(
            message="Date of birth",
        ),
    )
    phone = PhoneNumberField(
        verbose_name=_(
            message="Phone",
        ),
        blank=True,
    )

    # =========================================================
    #   PERMISSIONS DATA
    # =========================================================

    is_active = models.BooleanField(
        verbose_name=_(
            message="Is active",
        ),
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_(
            message="Is staff",
        ),
        default=False,
    )
    is_email_verified = models.BooleanField(
        verbose_name=_(
            message="Is email verified",
        ),
        default=False,
    )

    # =========================================================
    #   USER CONFIG
    # =========================================================

    objects: ClassVar[UserManagerModel] = UserManagerModel()

    USERNAME_FIELD: ClassVar[str] = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = [
        "name",
        "date_birth",
    ]

    class Meta:
        db_table = "user"
        verbose_name = _(message="User")
        verbose_name_plural = _(message="Users")
        ordering = ("email",)

    def __str__(
        self,
    ) -> str:
        name = cast(str, self.name)
        email = cast(str, self.email)

        return f"{name} <{email}>"

    def get_full_name(
        self,
    ) -> str:
        name = cast(str, self.name)
        return name

    def get_short_name(
        self,
    ) -> str:
        name = cast(str, self.name)
        return name.split(maxsplit=1)[0]

    def user_email_confirmation(
        self,
        subject: str,
        message: str,
        from_email: str | None = None,
        **kwargs: Any,
    ) -> None:

        email = cast(str, self.email)

        send_mail(
            subject,
            message,
            from_email,
            recipient_list=[
                email,
            ],
            **kwargs,
        )

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        name = cast(str, self.name)
        email = cast(str, self.email)

        if name:
            self.name = normalize_whitespace(name=name)
        if email:
            self.email = normalize_email(email)

        return super().save(*args, **kwargs)
