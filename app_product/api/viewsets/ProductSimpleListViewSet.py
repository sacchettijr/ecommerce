from typing import TYPE_CHECKING

from django.db.models import CharField, QuerySet, Value
from django.db.models.functions import MD5, Cast, Concat
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from app_core.api.filters import StableOrderingFilter
from app_product.api.filters import ProductFilterSet
from app_product.api.serializers import ProductSimpleListSerializer
from app_product.models import ProductModel

if TYPE_CHECKING:
    BaseProductListViewSet = viewsets.GenericViewSet[ProductModel]
else:
    BaseProductListViewSet = viewsets.GenericViewSet


class ProductSimpleListViewSet(
    mixins.ListModelMixin,
    BaseProductListViewSet,
):
    serializer_class = ProductSimpleListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        StableOrderingFilter,
    )
    filterset_class = ProductFilterSet
    search_fields = ("name",)
    ordering_fields = (
        "name",
        "price",
        "created_at",
    )
    #   Default order is a deterministic, daily-seeded shuffle (see "_shuffle" in
    #   get_queryset): avoids a recency bias that lets a single bulk-imported
    #   category dominate page 1 just because it was added most recently, without
    #   a per-request `?` random sort that would break pagination (duplicate or
    #   skipped products between pages). "_shuffle" isn't in ordering_fields, so an
    #   explicit, user-requested `ordering=` (name/price/created_at) still overrides
    #   it, exactly as before.
    ordering = ("_shuffle",)

    def get_queryset(self) -> QuerySet[ProductModel]:
        #   Same seed for every request within the same day: deterministic order,
        #   so paginating through results never repeats or skips a product. The
        #   seed changes once a day, which is enough to keep the catalog feeling
        #   varied without the cost/complexity of a per-visitor session seed.
        seed = timezone.now().date().isoformat()

        return ProductModel.objects.filter(
            active=True,
        ).annotate(
            _shuffle=MD5(
                Concat(
                    Cast("id", output_field=CharField()),
                    Value(seed),
                ),
            ),
        )
