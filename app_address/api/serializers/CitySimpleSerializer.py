from typing import TYPE_CHECKING

from rest_framework import serializers

from app_address.models import CityModel

if TYPE_CHECKING:
    BaseCitySimpleSerializer = serializers.ModelSerializer[CityModel]
else:
    BaseCitySimpleSerializer = serializers.ModelSerializer


class CitySimpleSerializer(BaseCitySimpleSerializer):
    #   Not a direct CityModel field - resolved through state.country_id so the
    #   admin's cascading JS can stamp a rebuilt <option> with the same
    #   data-country it would get from a server-rendered one (see
    #   CityLocationSelect / StateLocationSelect).
    country = serializers.IntegerField(source="state.country_id")

    class Meta:
        model = CityModel
        fields = (
            "id",
            "name",
            "state",
            "country",
        )
        read_only_fields = fields
