from __future__ import annotations

from collections.abc import Collection
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    cast,
)

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models.constraints import BaseConstraint
from django.db.models.fields.related import ForeignKey
from django.utils.translation import (
    gettext_lazy as _,
)

from app_address.models import BaseAddressModel

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

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        #   Por usuário (tudo na mesma transação, com o usuário travado para serializar
        #   operações concorrentes sobre os endereços dele): no máximo um principal;
        #   marcar este como principal desmarca os demais do mesmo usuário.
        user_id: int = cast(Any, self).user_id

        with transaction.atomic():
            get_user_model().objects.select_for_update().only("pk").get(pk=user_id)

            siblings = type(self).objects.filter(user_id=user_id)

            if cast(bool, self.primary):
                siblings.exclude(pk=self.pk).filter(primary=True).update(primary=False)

            super().save(*args, **kwargs)

    def validate_constraints(
        self,
        exclude: Collection[str] | None = None,
    ) -> None:
        #   primary é reorganizado pelo save(): marcar mais de um principal no formulário
        #   (Admin) não é erro, e a constraint do banco continua valendo.
        super().validate_constraints(exclude={*(exclude or ()), "primary"})

    def _get_unique_checks(
        self,
        exclude: Collection[str] | None = None,
        include_meta_constraints: bool = False,
    ) -> tuple[list[Any], list[Any]]:
        #   _get_unique_checks é a API privada que o BaseModelFormSet usa; não está nos stubs.
        unique_checks, date_checks = cast(Any, super())._get_unique_checks(
            exclude=exclude,
            include_meta_constraints=include_meta_constraints,
        )
        #   O formset do inline também consulta as constraints: tira a de primary pelo mesmo motivo.
        return (
            [check for check in unique_checks if set(check[1]) != {"user"}],
            date_checks,
        )
