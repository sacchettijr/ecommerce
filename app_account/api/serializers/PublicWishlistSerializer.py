from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from rest_framework import serializers

from app_account.models import (
    UserWishlistItemModel,
    UserWishlistModel,
)

from .PublicWishlistItemSerializer import PublicWishlistItemSerializer

if TYPE_CHECKING:
    BasePublicWishlistSerializer = serializers.ModelSerializer[UserWishlistModel]
else:
    BasePublicWishlistSerializer = serializers.ModelSerializer


class PublicWishlistSerializer(BasePublicWishlistSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = UserWishlistModel
        fields = (
            "public_id",
            "items",
        )
        read_only_fields = fields

    def get_items(self, wishlist: UserWishlistModel) -> list[dict[str, Any]]:
        request = self.context.get("request")
        viewer_is_staff = bool(
            request is not None and request.user.is_staff,
        )

        public_items = UserWishlistItemModel.objects.filter(
            wishlist=wishlist,
            private=False,
        ).select_related(
            "product",
        )

        if not viewer_is_staff:
            public_items = public_items.exclude(
                product__active=False,
            )

        return cast(
            list[dict[str, Any]],
            PublicWishlistItemSerializer(
                instance=public_items,
                many=True,
            ).data,
        )
