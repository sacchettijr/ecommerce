from typing import TYPE_CHECKING, Any, cast

from rest_framework import serializers

from app_account.models import UserWishlistItemModel, UserWishlistModel

from .PublicWishlistItemSerializer import PublicWishlistItemSerializer

if TYPE_CHECKING:
    BasePublicWishlistSerializer = serializers.ModelSerializer[UserWishlistModel]
else:
    BasePublicWishlistSerializer = serializers.ModelSerializer


class PublicWishlistSerializer(BasePublicWishlistSerializer):
    """Read shape for a third party's wishlist, looked up by its opaque public_id."""

    items = serializers.SerializerMethodField()

    class Meta:
        model = UserWishlistModel
        fields = (
            "public_id",
            "items",
        )
        read_only_fields = fields

    def get_items(self, wishlist: UserWishlistModel) -> list[dict[str, Any]]:
        public_items = UserWishlistItemModel.objects.filter(
            wishlist=wishlist,
            private=False,
        ).select_related("product")
        return cast(
            list[dict[str, Any]],
            PublicWishlistItemSerializer(public_items, many=True).data,
        )
