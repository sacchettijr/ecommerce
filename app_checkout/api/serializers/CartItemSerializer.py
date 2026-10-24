from decimal import Decimal
from typing import TYPE_CHECKING, cast

from rest_framework import serializers

from app_checkout.models import CartItemModel
from app_product.api.serializers import ProductSimpleListSerializer
from app_product.models import ProductModel

if TYPE_CHECKING:
    BaseCartItemSerializer = serializers.ModelSerializer[CartItemModel]
else:
    BaseCartItemSerializer = serializers.ModelSerializer


class CartItemSerializer(BaseCartItemSerializer):
    product = ProductSimpleListSerializer(
        read_only=True,
    )
    unit_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItemModel
        fields = (
            "id",
            "product",
            "quantity",
            "unit_price",
            "line_total",
        )
        read_only_fields = fields

    def get_unit_price(self, cart_item: CartItemModel) -> str:
        product = cast(
            ProductModel,
            cart_item.product,
        )
        return str(
            cast(
                Decimal,
                product.price,
            )
        )

    def get_line_total(
        self,
        cart_item: CartItemModel,
    ) -> str:
        product = cast(
            ProductModel,
            cart_item.product,
        )
        quantity = cast(
            int,
            cart_item.quantity,
        )
        return str(
            cast(
                Decimal,
                product.price,
            )
            * quantity
        )
