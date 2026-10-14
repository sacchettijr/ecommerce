from typing import TYPE_CHECKING

from rest_framework import serializers

from app_address.models import StateModel

if TYPE_CHECKING:
    BaseStateSimpleSerializer = serializers.ModelSerializer[StateModel]
else:
    BaseStateSimpleSerializer = serializers.ModelSerializer


class StateSimpleSerializer(BaseStateSimpleSerializer):
    class Meta:
        model = StateModel
        fields = (
            "id",
            "name",
            "code",
        )
        read_only_fields = fields
