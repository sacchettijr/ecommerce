from django_filters.rest_framework import (
    CharFilter,
    FilterSet,
)

from product.models import ProductModel


class ProductFilterSet(FilterSet):
    category = CharFilter(
        field_name="category__slug",
    )

    class Meta:
        model = ProductModel
        fields = ("category",)
