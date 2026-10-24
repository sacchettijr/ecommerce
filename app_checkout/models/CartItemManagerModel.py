from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    cast,
)

from django.db import models

from app_product.models import ProductModel

if TYPE_CHECKING:
    from .CartItemModel import CartItemModel

    BaseCartItemManager = models.Manager[CartItemModel]
else:
    BaseCartItemManager = models.Manager


class CartItemManagerModel(BaseCartItemManager):
    def add_item(
        self,
        cart_key: str,
        product: ProductModel,
    ) -> tuple[CartItemModel, bool]:

        cart_item = self.filter(
            cart_key=cart_key,
            product=product,
        ).first()

        if cart_item is not None:
            cart_item.quantity = (
                cast(
                    int,
                    cart_item.quantity,
                )
                + 1
            )
            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                    "updated_by",
                ],
            )
            return cart_item, False

        cart_item = CartItemModel.objects.create(
            cart_key=cart_key,
            product=product,
            price=cast(
                Decimal,
                product.price,
            ),
        )

        return cart_item, True
