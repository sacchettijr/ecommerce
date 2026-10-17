from typing import TYPE_CHECKING

from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from app_account.api.serializers import PublicWishlistSerializer
from app_account.models import UserWishlistModel

if TYPE_CHECKING:
    BasePublicWishlistViewSet = viewsets.GenericViewSet[UserWishlistModel]
else:
    BasePublicWishlistViewSet = viewsets.GenericViewSet


class PublicWishlistViewSet(
    mixins.RetrieveModelMixin,
    BasePublicWishlistViewSet,
):
    """A third party's wishlist, looked up by its opaque public_id.

    AllowAny: any visitor, authenticated or not, may view a public wishlist. The wishlist
    row itself isn't secret — only its private items are, and PublicWishlistSerializer
    already excludes those before serialization, so nothing private ever reaches this
    response regardless of who's asking.
    """

    permission_classes = (AllowAny,)
    serializer_class = PublicWishlistSerializer
    lookup_field = "public_id"
    lookup_url_kwarg = "public_id"

    def get_queryset(self) -> QuerySet[UserWishlistModel]:
        return UserWishlistModel.objects.all()
