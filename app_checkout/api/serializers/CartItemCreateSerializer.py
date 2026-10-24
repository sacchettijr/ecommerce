from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from rest_framework import serializers

from app_checkout.models import CartItemModel
from app_product.models import ProductModel

if TYPE_CHECKING:
    from app_account.models.UserModel import UserModel

    BaseCartItemCreateSerializer = serializers.ModelSerializer[CartItemModel]
else:
    BaseCartItemCreateSerializer = serializers.ModelSerializer


class CartItemCreateSerializer(BaseCartItemCreateSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=ProductModel.objects.filter(
            active=True,
        ),
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )

    class Meta:
        model = CartItemModel
        fields = (
            "product",
            "quantity",
        )

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> CartItemModel:
        user = cast(
            "UserModel",
            self.context["request"].user,
        )
        return CartItemModel.objects.add_item(
            user=user,
            product=validated_data["product"],
            quantity=validated_data["quantity"],
        )
