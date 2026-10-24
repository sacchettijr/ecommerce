from typing import Any, cast

from django.db.models.signals import post_save
from django.dispatch import receiver

from app_checkout.models import CartItemModel
from app_product.models import ProductModel


@receiver(
    signal=post_save,
    sender=ProductModel,
)
def remove_product_from_carts_when_deactivated(
    sender: type[ProductModel],
    instance: ProductModel,
    **kwargs: Any,
) -> None:
    if (
        cast(
            bool,
            instance.active,
        )
        is False
    ):
        CartItemModel.objects.filter(
            product=instance,
        ).delete()
