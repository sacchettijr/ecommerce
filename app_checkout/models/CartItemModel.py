from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    ClassVar,
    cast,
)

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.translation import (
    gettext_lazy as _,
)

from app_core.models import BaseModel
from app_product.models import ProductModel
from utils.validator import (
    validate_positive_decimal,
)

from .CartItemManagerModel import CartItemManagerModel

if TYPE_CHECKING:
    from app_account.models import UserModel


class CartItemModel(BaseModel):
    user: ForeignKey[UserModel, UserModel] = models.ForeignKey(
        to="account.UserModel",
        verbose_name=_(
            message="User",
        ),
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(
        to=ProductModel,
        verbose_name=_(
            message="Product",
        ),
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_(
            message="Quantity",
        ),
        default=1,
        validators=[
            MinValueValidator(limit_value=1),
        ],
    )
    price = models.DecimalField(
        verbose_name=_(
            message="Price",
        ),
        decimal_places=2,
        max_digits=10,
        validators=[
            validate_positive_decimal,
        ],
    )

    objects: ClassVar[CartItemManagerModel] = CartItemManagerModel()

    class Meta:
        db_table = "cart_item"
        verbose_name = _(
            message="Cart Item",
        )
        verbose_name_plural = _(
            message="Cart Items",
        )
        unique_together = (
            (
                "user",
                "product",
            ),
        )

    def __str__(self) -> str:
        product = cast(
            str,
            self.product,
        )
        quantity = cast(
            int,
            self.quantity,
        )

        return f"{product} [{quantity}]"

    # def __init__(
    #     self,
    #     product_id,
    #     quantity,
    # ) -> None:
    #     self.product_id = product_id
    #     self.quantity = quantity

    # def to_dict(self) -> dict[str, Any]:
    #     return {
    #         "product_id": self.product_id,
    #         "quantity": self.quantity,
    #     }
