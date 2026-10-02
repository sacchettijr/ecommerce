from typing import TYPE_CHECKING

from django.db.models import QuerySet
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.permissions import AllowAny

from product.api.serializers import ProductDetailSerializer
from product.models import ProductModel

if TYPE_CHECKING:
    BaseProductDetailViewSet = viewsets.GenericViewSet[ProductModel]
else:
    BaseProductDetailViewSet = viewsets.GenericViewSet


class ProductDetailViewSet(
    mixins.RetrieveModelMixin,
    BaseProductDetailViewSet,
):
    serializer_class = ProductDetailSerializer
    permission_classes = (AllowAny,)
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[ProductModel]:
        #   Produto inativo não existe para a API pública: o get_object() devolve 404.
        return (
            ProductModel.objects.filter(
                active=True,
            )
            .select_related("category")
            .prefetch_related("images")
        )
