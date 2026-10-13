from typing import TYPE_CHECKING

from django.db.models import QuerySet
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
    ordering = ("-created_at",)

    def get_queryset(self) -> QuerySet[ProductModel]:
        return ProductModel.objects.filter(
            active=True,
        )
