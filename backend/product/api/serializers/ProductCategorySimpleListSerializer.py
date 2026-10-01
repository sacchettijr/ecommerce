from typing import TYPE_CHECKING

from rest_framework import serializers

from product.models import ProductCategoryModel

if TYPE_CHECKING:
    BaseProductListSerializer = serializers.ModelSerializer[ProductCategoryModel]
else:
    BaseProductListSerializer = serializers.ModelSerializer


class ProductCategorySimpleListSerializer(BaseProductListSerializer):
    class Meta:
        model = ProductCategoryModel
        fields = (
            "id",
            "name",
            "slug",
        )
