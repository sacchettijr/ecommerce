from typing import TYPE_CHECKING

from rest_framework import serializers

from product.models import ProductModel

from .ProductCategorySimpleListSerializer import ProductCategorySimpleListSerializer
from .ProductImageSimpleSerializer import ProductImageSimpleSerializer

if TYPE_CHECKING:
    BaseProductDetailSerializer = serializers.ModelSerializer[ProductModel]
else:
    BaseProductDetailSerializer = serializers.ModelSerializer


class ProductDetailSerializer(BaseProductDetailSerializer):
    category = ProductCategorySimpleListSerializer(
        read_only=True,
    )
    images = ProductImageSimpleSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProductModel
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "description",
            "price",
            "images",
        )
