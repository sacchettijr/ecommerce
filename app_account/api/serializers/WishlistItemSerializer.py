from typing import TYPE_CHECKING

from rest_framework import serializers

from app_account.models import UserWishlistItemModel
from app_product.api.serializers import ProductSimpleListSerializer

if TYPE_CHECKING:
    BaseWishlistItemSerializer = serializers.ModelSerializer[UserWishlistItemModel]
else:
    BaseWishlistItemSerializer = serializers.ModelSerializer


class WishlistItemSerializer(BaseWishlistItemSerializer):
    """Read shape for the authenticated owner's own wishlist (includes private items)."""

    product = ProductSimpleListSerializer(read_only=True)

    class Meta:
        model = UserWishlistItemModel
        fields = (
            "id",
            "product",
            "added_at",
            "position",
            "private",
        )
        read_only_fields = fields
