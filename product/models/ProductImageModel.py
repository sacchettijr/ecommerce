from collections.abc import Collection
from typing import (
    Any,
    ClassVar,
    cast,
)

from django.db import (
    models,
    transaction,
)
from django.utils.translation import (
    gettext_lazy as _,
)

from core.models import BaseModel

from .organize_product_images import organize_product_images
from .product_image_upload_to import product_image_upload_to
from .ProductModel import ProductModel


class ProductImageModel(BaseModel):
    product = models.ForeignKey(
        to=ProductModel,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_(
            message="Product",
        ),
    )
    image = models.ImageField(
        verbose_name=_(
            message="Image",
        ),
        upload_to=product_image_upload_to,
        max_length=500,
    )
    is_primary = models.BooleanField(
        verbose_name=_(
            message="Primary image",
        ),
        default=False,
    )
    order = models.PositiveIntegerField(
        verbose_name=_(
            message="Order",
        ),
        default=0,
    )

    class Meta:
        db_table = "product_image"
        verbose_name = _(
            message="Product image",
        )
        verbose_name_plural = _(
            message="Products images",
        )
        ordering = (
            "order",
            "id",
        )
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("product",),
                condition=models.Q(is_primary=True),
                name="unique_primary_image_per_product",
            ),
            #   DEFERRED: a reorganização desloca várias imagens no mesmo UPDATE/transação,
            #   e a unicidade só precisa valer quando a transação termina.
            models.UniqueConstraint(
                fields=("product", "order"),
                name="unique_image_order_per_product",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def __str__(self) -> str:
        product = cast(int, self.product)
        order = cast(int, self.order)
        return f"{product} (#{order})"

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        #   Regras por produto (tudo na mesma transação, com o produto travado para serializar
        #   operações concorrentes sobre as imagens dele):
        #     - is_primary: só uma; marcar esta desmarca as demais.
        #     - order: sem repetição nem buracos, sempre 0, 1, 2...
        product_id: int = cast(Any, self).product_id
        previous_product_id = (
            None
            if self._state.adding
            else (
                type(self).objects.filter(pk=self.pk).values_list("product_id", flat=True).first()
            )
        )

        with transaction.atomic():
            ProductModel.objects.select_for_update().only("pk").get(pk=product_id)

            siblings = type(self).objects.filter(product_id=product_id)

            if cast(bool, self.is_primary):
                siblings.exclude(pk=self.pk).filter(is_primary=True).update(
                    is_primary=False,
                )

            super().save(*args, **kwargs)
            organize_product_images(siblings, anchor=self)

            #   Imagem movida para outro produto: o de origem também precisa fechar o buraco.
            if previous_product_id is not None and previous_product_id != product_id:
                organize_product_images(
                    type(self).objects.filter(product_id=previous_product_id),
                )

    def validate_constraints(
        self,
        exclude: Collection[str] | None = None,
    ) -> None:
        #   order e is_primary são reorganizados pelo save(): repetir order ou marcar outra
        #   principal no formulário (Admin) não é erro, e a constraint do banco continua valendo.
        super().validate_constraints(exclude={*(exclude or ()), "order", "is_primary"})

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
        #   O formset do inline também consulta as constraints: tira a de order pelo mesmo motivo.
        return (
            [check for check in unique_checks if set(check[1]) != {"product", "order"}],
            date_checks,
        )
