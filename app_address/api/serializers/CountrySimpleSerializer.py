from typing import TYPE_CHECKING

from rest_framework import serializers

from app_address.models import CountryModel

if TYPE_CHECKING:
    BaseCountrySimpleSerializer = serializers.ModelSerializer[CountryModel]
else:
    BaseCountrySimpleSerializer = serializers.ModelSerializer


class CountrySimpleSerializer(BaseCountrySimpleSerializer):
    class Meta:
        model = CountryModel
        fields = (
            "id",
            "name",
            "iso_code",
        )
        read_only_fields = fields
