from typing import TYPE_CHECKING, Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app_account.models import UserWishlistItemModel
from app_product.models import ProductModel

if TYPE_CHECKING:
    BaseWishlistItemCreateSerializer = serializers.ModelSerializer[UserWishlistItemModel]
else:
    BaseWishlistItemCreateSerializer = serializers.ModelSerializer


class WishlistItemCreateSerializer(BaseWishlistItemCreateSerializer):
    """Write shape for adding a product to the authenticated user's own wishlist.

    The wishlist itself is never a field here — the viewset injects it from
    ``request.user``, so a client can never choose whose wishlist a product is added to.
    """

    product = serializers.PrimaryKeyRelatedField(
        queryset=ProductModel.objects.filter(active=True),
    )

    class Meta:
        model = UserWishlistItemModel
        fields = ("product",)

    def validate_product(self, product: ProductModel) -> ProductModel:
        wishlist = self.context["wishlist"]

        if UserWishlistItemModel.objects.filter(wishlist=wishlist, product=product).exists():
            raise ValidationError(
                _(message="This product is already in your wishlist."),
            )

        return product

    def create(self, validated_data: dict[str, Any]) -> UserWishlistItemModel:
        validated_data["wishlist"] = self.context["wishlist"]
        return super().create(validated_data)
