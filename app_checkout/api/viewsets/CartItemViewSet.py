from typing import (
    Any,
    cast,
)

from django.db.models import QuerySet
from rest_framework import (
    mixins,
    status,
    viewsets,
)
from rest_framework.request import Request
from rest_framework.response import Response

from app_account.models import UserModel
from app_checkout.api.serializers import (
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CartSummarySerializer,
)
from app_checkout.models import CartItemModel

BaseCartItemViewSet = viewsets.GenericViewSet


class CartItemViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseCartItemViewSet,
):
    pagination_class = None

    def get_queryset(self) -> QuerySet[CartItemModel]:
        user = cast(
            UserModel,
            self.request.user,
        )
        return CartItemModel.objects.filter(
            user=user,
        ).select_related(
            "product",
        )

    def get_serializer_class(
        self,
    ) -> type[CartItemCreateSerializer | CartItemUpdateSerializer | CartSummarySerializer]:
        if self.action == "create":
            return CartItemCreateSerializer
        if self.action in ("update", "partial_update"):
            return CartItemUpdateSerializer
        return CartSummarySerializer

    def _summary_response(
        self,
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        user = cast(
            UserModel,
            self.request.user,
        )
        summary = CartItemModel.objects.summary_for(user)
        return Response(
            data=cast(
                dict[str, Any],
                CartSummarySerializer(
                    instance=summary,
                ).data,
            ),
            status=status_code,
        )

    def list(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        return self._summary_response()

    def create(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save()

        return self._summary_response(
            status_code=status.HTTP_201_CREATED,
        )

    def update(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        partial = kwargs.pop(
            "partial",
            False,
        )
        instance = cast(
            CartItemModel,
            self.get_object(),
        )
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save()

        return self._summary_response()

    def destroy(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        instance = cast(
            CartItemModel,
            self.get_object(),
        )
        instance.delete()

        return self._summary_response()
