from typing import TYPE_CHECKING, Any, cast

from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app_account.api.serializers import UserAddressSerializer
from app_account.models import UserAddressModel, UserModel

if TYPE_CHECKING:
    BaseUserAddressViewSet = viewsets.GenericViewSet[UserAddressModel]
else:
    BaseUserAddressViewSet = viewsets.GenericViewSet


class UserAddressViewSet(
    mixins.ListModelMixin,
    BaseUserAddressViewSet,
):
    #   Uses the project's default IsAuthenticated permission (no AllowAny override). The
    #   queryset is always scoped to request.user — no user/address identifier from the
    #   request can ever surface another user's addresses, and get_object() (used by
    #   set_primary) 404s instead of leaking whether an address belonging to someone else
    #   exists. A handful of addresses per user doesn't need the project's default page-based
    #   pagination, so it's disabled here (the response is a plain array).
    serializer_class = UserAddressSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[UserAddressModel]:
        user = cast(UserModel, self.request.user)

        #   Primary first, regardless of the model's own Meta.ordering (which sorts primary
        #   last, since False < True) — the primary address is what a user expects to see first.
        return (
            UserAddressModel.objects.filter(user=user)
            .select_related("city", "state", "country")
            .order_by("-primary", "created_at")
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="set-primary",
    )
    def set_primary(
        self,
        request: Request,
        pk: str | None = None,
    ) -> Response:
        address = self.get_object()

        if not cast(bool, address.primary):
            address.primary = True
            #   UserAddressModel.save() demotes every other address of this user atomically.
            address.save(update_fields=["primary"])

        return Response(
            data=cast(
                list[dict[str, Any]],
                UserAddressSerializer(self.get_queryset(), many=True).data,
            ),
        )
