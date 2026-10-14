from typing import TYPE_CHECKING

from rest_framework import serializers

from app_address.models import CityModel

if TYPE_CHECKING:
    BaseCitySimpleSerializer = serializers.ModelSerializer[CityModel]
else:
    BaseCitySimpleSerializer = serializers.ModelSerializer


class CitySimpleSerializer(BaseCitySimpleSerializer):
    class Meta:
        model = CityModel
        fields = (
            "id",
            "name",
        )
        read_only_fields = fields
