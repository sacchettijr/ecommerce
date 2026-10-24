from dataclasses import dataclass, field
from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    cast,
)

from django.contrib.auth import get_user_model
from django.db import models, transaction

from app_product.models import ProductModel

if TYPE_CHECKING:
    from app_account.models.UserModel import UserModel

    from .CartItemModel import CartItemModel

    BaseCartItemManager = models.Manager[CartItemModel]
else:
    BaseCartItemManager = models.Manager


@dataclass(frozen=True)
class CartSummary:
    items: list[CartItemModel] = field(
        default_factory=list,
    )
    subtotal: Decimal = Decimal(
        value="0.00",
    )
    discount_total: Decimal = Decimal(
        value="0.00",
    )
    total: Decimal = Decimal(
        value="0.00",
    )


class CartItemManagerModel(BaseCartItemManager):
    def add_item(
        self,
        user: UserModel,
        product: ProductModel,
        *,
        quantity: int = 1,
    ) -> CartItemModel:
        with transaction.atomic():
            get_user_model().objects.select_for_update().only("pk").get(
                pk=user.pk,
            )

            cart_item, created = self.get_or_create(
                user=user,
                product=product,
                defaults={
                    "quantity": quantity,
                    "price": cast(
                        Decimal,
                        product.price,
                    ),
                },
            )

            if not created:
                cart_item.quantity = cast(int, cart_item.quantity) + quantity
                cart_item.price = cast(
                    Decimal,
                    product.price,
                )
                cart_item.save(
                    update_fields=[
                        "quantity",
                        "price",
                        "updated_at",
                        "updated_by",
                    ],
                )

        return cart_item

    def summary_for(
        self,
        user: UserModel,
    ) -> CartSummary:
        items = list(
            self.filter(
                user=user,
            )
            .select_related(
                "product",
            )
            .order_by(
                "created_at",
            )
        )

        subtotal = sum(
            (
                cast(
                    Decimal,
                    cast(
                        ProductModel,
                        item.product,
                    ).price,
                )
                * cast(
                    int,
                    item.quantity,
                )
                for item in items
            ),
            start=Decimal(
                value="0.00",
            ),
        )
        discount_total = Decimal(
            value="0.00",
        )

        return CartSummary(
            items=items,
            subtotal=subtotal,
            discount_total=discount_total,
            total=subtotal - discount_total,
        )
