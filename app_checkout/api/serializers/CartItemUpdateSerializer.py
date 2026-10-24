from typing import TYPE_CHECKING

from rest_framework import serializers

from app_checkout.models import CartItemModel

if TYPE_CHECKING:
    BaseCartItemUpdateSerializer = serializers.ModelSerializer[CartItemModel]
else:
    BaseCartItemUpdateSerializer = serializers.ModelSerializer


class CartItemUpdateSerializer(BaseCartItemUpdateSerializer):
    quantity = serializers.IntegerField(
        min_value=1,
    )

    class Meta:
        model = CartItemModel
        fields = ("quantity",)
