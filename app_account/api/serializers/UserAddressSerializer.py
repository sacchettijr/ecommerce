from typing import TYPE_CHECKING

from rest_framework import serializers

from app_account.models import UserAddressModel
from app_address.api.serializers import (
    CitySimpleSerializer,
    CountrySimpleSerializer,
    StateSimpleSerializer,
)

if TYPE_CHECKING:
    BaseUserAddressSerializer = serializers.ModelSerializer[UserAddressModel]
else:
    BaseUserAddressSerializer = serializers.ModelSerializer


class UserAddressSerializer(BaseUserAddressSerializer):
    city = CitySimpleSerializer(read_only=True)
    state = StateSimpleSerializer(read_only=True)
    country = CountrySimpleSerializer(read_only=True)

    class Meta:
        model = UserAddressModel
        fields = (
            "id",
            "street",
            "number",
            "complement",
            "reference",
            "district",
            "postal_code",
            "city",
            "state",
            "country",
            "primary",
        )
        read_only_fields = fields
