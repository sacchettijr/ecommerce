from typing import TYPE_CHECKING

from rest_framework import serializers

from product.models import ProductImageModel

if TYPE_CHECKING:
    BaseProductImageSerializer = serializers.ModelSerializer[ProductImageModel]
else:
    BaseProductImageSerializer = serializers.ModelSerializer


class ProductImageSimpleSerializer(BaseProductImageSerializer):
    class Meta:
        model = ProductImageModel
        fields = (
            "id",
            "image",
        )
