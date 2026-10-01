from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.current_user import (
    get_current_user,
)

if TYPE_CHECKING:
    from account.models.UserModel import UserModel


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_(
            message="Created at",
        ),
        auto_now_add=True,
        null=True,
        blank=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_(
            message="Updated at",
        ),
        auto_now=True,
        null=True,
        blank=True,
        editable=False,
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_(
            message="Created by",
        ),
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        null=True,
        blank=True,
        editable=False,
    )
    updated_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_(
            message="Update by",
        ),
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        user = get_current_user()

        if user:
            user = cast("UserModel", user)

            created_by = cast(
                "UserModel | None",
                self.created_by,
            )

            self.created_by = created_by or user
            self.updated_by = user

        return super().save(*args, **kwargs)
