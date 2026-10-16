from typing import TYPE_CHECKING

from django.db.models import QuerySet
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.permissions import IsAdminUser

from app_address.api.serializers import CitySimpleSerializer
from app_address.models import CityModel

if TYPE_CHECKING:
    BaseCityListViewSet = viewsets.GenericViewSet[CityModel]
else:
    BaseCityListViewSet = viewsets.GenericViewSet


class CityListViewSet(
    mixins.ListModelMixin,
    BaseCityListViewSet,
):
    #   Backs the Django Admin's state -> city cascading dropdown only, so this is
    #   restricted to staff rather than AllowAny like the public product endpoints.
    serializer_class = CitySimpleSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = None

    def get_queryset(self) -> QuerySet[CityModel]:
        #   select_related("state"): the serializer resolves "country" through
        #   state.country_id for every row - avoid an N+1 query for it.
        queryset = CityModel.objects.select_related("state").order_by("name")
        state_id = self.request.query_params.get("state")

        if state_id is not None:
            try:
                queryset = queryset.filter(state_id=int(state_id))
            except ValueError:
                return queryset.none()

        return queryset
