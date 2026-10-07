from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    ClassVar,
)

from django.db import models
from django.db.models.constraints import BaseConstraint
from django.db.models.fields.related import ForeignKey
from django.utils.translation import (
    gettext_lazy as _,
)

from address.models import BaseAddressModel

if TYPE_CHECKING:
    from .UserModel import UserModel


class UserAddressModel(BaseAddressModel):
    user: ForeignKey[UserModel, UserModel] = models.ForeignKey(
        to="account.UserModel",
        on_delete=models.CASCADE,
        related_name="user_addresses",
    )

    primary = models.BooleanField(
        verbose_name=_(
            message="Primary",
        ),
        default=False,
    )

    class Meta:
        db_table = "user_addresses"
        verbose_name = _(message="User Address")
        verbose_name_plural = _(message="User Addresses")
        ordering = (
            "user",
            "primary",
            "created_at",
        )
        constraints: ClassVar[list[BaseConstraint]] = [
            models.UniqueConstraint(
                fields=[
                    "user",
                ],
                condition=models.Q(
                    primary=True,
                ),
                name="unique_primary_address_per_user",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.user} - {self.street}, {self.number}, "
            f"{self.complement}, {self.reference}, {self.district}, "
            f"{self.postal_code}, {self.city}, {self.state}, {self.country}"
        )
