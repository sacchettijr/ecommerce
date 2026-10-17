from typing import TYPE_CHECKING, Any, cast

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app_account.api.serializers import (
    WishlistItemCreateSerializer,
    WishlistItemSerializer,
)
from app_account.models import UserModel, UserWishlistItemModel, UserWishlistModel

if TYPE_CHECKING:
    BaseWishlistItemViewSet = viewsets.GenericViewSet[UserWishlistItemModel]
else:
    BaseWishlistItemViewSet = viewsets.GenericViewSet


class WishlistItemViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseWishlistItemViewSet,
):
    """The authenticated user's own wishlist items (includes private ones).

    Uses the project's default IsAuthenticated permission (no AllowAny override). Every
    queryset below is scoped to request.user — no wishlist/user id from the request can ever
    surface or mutate another user's items, and get_object() 404s instead of leaking whether
    an item belonging to someone else exists (same pattern as UserAddressViewSet).
    """

    pagination_class = None

    def get_queryset(self) -> QuerySet[UserWishlistItemModel]:
        user = cast(UserModel, self.request.user)
        return UserWishlistItemModel.objects.filter(
            wishlist__user=user,
        ).select_related("product")

    def get_serializer_class(self) -> type[WishlistItemSerializer | WishlistItemCreateSerializer]:
        if self.action == "create":
            return WishlistItemCreateSerializer
        return WishlistItemSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())

        if self.action == "create":
            user = cast(UserModel, self.request.user)
            wishlist, _ = UserWishlistModel.objects.get_or_create(user=user)
            context["wishlist"] = wishlist

        return context

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data=cast(
                list[dict[str, Any]],
                WishlistItemSerializer(self.get_queryset(), many=True).data,
            ),
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        instance.delete()

        #   UserWishlistItemModel's own post_delete signal already reorganizes the
        #   remaining items' positions — no ordering logic duplicated here.
        return Response(
            data=cast(
                list[dict[str, Any]],
                WishlistItemSerializer(self.get_queryset(), many=True).data,
            ),
        )

    @action(detail=True, methods=["post"], url_path="toggle-privacy")
    def toggle_privacy(self, request: Request, pk: str | None = None) -> Response:
        item = self.get_object()
        item.private = not cast(bool, item.private)
        item.save(update_fields=["private"])

        return Response(
            data=cast(
                list[dict[str, Any]],
                WishlistItemSerializer(self.get_queryset(), many=True).data,
            ),
        )

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request: Request, pk: str | None = None) -> Response:
        item = self.get_object()
        body = cast(dict[str, Any], request.data)
        direction = body.get("direction")

        if direction not in ("up", "down"):
            return Response(
                data={"direction": ['Must be "up" or "down".']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        #   Deliberately NOT reusing organize_wishlist_items()/UserWishlistItemModel.save()
        #   here: that anchor-insert algorithm assumes the *other* items are already
        #   gapless once the anchor is excluded, which only holds for the create/append
        #   case. For an in-place move, excluding the anchor leaves a gap at its old slot,
        #   and inserting it back by "first sibling position >= target" silently
        #   recomputes the anchor right back to where it started for an adjacent swap —
        #   confirmed by test before writing this. A plain adjacent swap, locking the
        #   wishlist the same way the rest of this app's reorganizers do, is the correct
        #   primitive for "move up/down by one" and isn't duplicated anywhere else.
        with transaction.atomic():
            wishlist_id = cast(Any, item).wishlist_id
            UserWishlistModel.objects.select_for_update().only("pk").get(pk=wishlist_id)

            siblings = self.get_queryset().order_by("position")
            position = cast(int, item.position)
            neighbor = (
                siblings.filter(position__lt=position).order_by("-position").first()
                if direction == "up"
                else siblings.filter(position__gt=position).order_by("position").first()
            )

            if neighbor is not None:
                neighbor_position = cast(int, neighbor.position)
                UserWishlistItemModel.objects.filter(pk=item.pk).update(
                    position=neighbor_position,
                )
                UserWishlistItemModel.objects.filter(pk=neighbor.pk).update(
                    position=position,
                )

        return Response(
            data=cast(
                list[dict[str, Any]],
                WishlistItemSerializer(self.get_queryset(), many=True).data,
            ),
        )

    @action(detail=False, methods=["get"], url_path="check")
    def check(self, request: Request) -> Response:
        raw_product_id = request.query_params.get("product")

        if raw_product_id is None:
            return Response(
                data={"product": ["This query parameter is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product_id = int(raw_product_id)
        except ValueError:
            return Response(
                data={"product": ["Must be a valid product id."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = self.get_queryset().filter(product_id=product_id).first()

        return Response(
            data={
                "in_wishlist": item is not None,
                "item_id": item.pk if item is not None else None,
            },
        )

    @action(detail=False, methods=["get"], url_path="share-link")
    def share_link(self, request: Request) -> Response:
        user = cast(UserModel, request.user)
        wishlist, _ = UserWishlistModel.objects.get_or_create(user=user)
        public_id = cast(Any, wishlist).public_id

        return Response(
            data={"public_id": str(public_id)},
        )
