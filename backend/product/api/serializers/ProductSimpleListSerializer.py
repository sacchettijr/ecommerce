from typing import TYPE_CHECKING

from rest_framework import serializers

from product.models import ProductModel

if TYPE_CHECKING:
    BaseProductListSerializer = serializers.ModelSerializer[ProductModel]
else:
    BaseProductListSerializer = serializers.ModelSerializer


class ProductSimpleListSerializer(BaseProductListSerializer):
    class Meta:
        model = ProductModel
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "thumbnail",
        )
