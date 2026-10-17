from typing import TYPE_CHECKING

from rest_framework import serializers

from app_account.models import UserWishlistItemModel
from app_product.api.serializers import ProductSimpleListSerializer

if TYPE_CHECKING:
    BasePublicWishlistItemSerializer = serializers.ModelSerializer[UserWishlistItemModel]
else:
    BasePublicWishlistItemSerializer = serializers.ModelSerializer


class PublicWishlistItemSerializer(BasePublicWishlistItemSerializer):
    """Read shape for a third party viewing someone else's wishlist.

    Deliberately has no ``private`` field — the queryset that feeds this serializer already
    excludes private items (see PublicWishlistSerializer), so there is nothing to flag.
    """

    product = ProductSimpleListSerializer(read_only=True)

    class Meta:
        model = UserWishlistItemModel
        fields = (
            "id",
            "product",
            "added_at",
            "position",
        )
        read_only_fields = fields
