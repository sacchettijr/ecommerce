from typing import TYPE_CHECKING

from django.db.models import QuerySet
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.permissions import AllowAny

from product.api.serializers import ProductCategorySimpleListSerializer
from product.models import ProductCategoryModel

if TYPE_CHECKING:
    BaseProductListViewSet = viewsets.GenericViewSet[ProductCategoryModel]
else:
    BaseProductListViewSet = viewsets.GenericViewSet


class ProductCategorySimpleListViewSet(
    mixins.ListModelMixin,
    BaseProductListViewSet,
):
    serializer_class = ProductCategorySimpleListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self) -> QuerySet[ProductCategoryModel]:
        return ProductCategoryModel.objects.filter(
            active=True,
        )
