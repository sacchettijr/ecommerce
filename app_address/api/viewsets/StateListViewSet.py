from typing import TYPE_CHECKING

from django.db.models import QuerySet
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.permissions import IsAdminUser

from app_address.api.serializers import StateSimpleSerializer
from app_address.models import StateModel

if TYPE_CHECKING:
    BaseStateListViewSet = viewsets.GenericViewSet[StateModel]
else:
    BaseStateListViewSet = viewsets.GenericViewSet


class StateListViewSet(
    mixins.ListModelMixin,
    BaseStateListViewSet,
):
    #   Backs the Django Admin's country -> state cascading dropdown only, so this is
    #   restricted to staff rather than AllowAny like the public product endpoints.
    serializer_class = StateSimpleSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = None

    def get_queryset(self) -> QuerySet[StateModel]:
        queryset = StateModel.objects.order_by("name")
        country_id = self.request.query_params.get("country")

        if country_id is not None:
            try:
                queryset = queryset.filter(country_id=int(country_id))
            except ValueError:
                return queryset.none()

        return queryset
