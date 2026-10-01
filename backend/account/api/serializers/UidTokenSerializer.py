from typing import Any

from rest_framework import serializers


class UidTokenSerializer(serializers.Serializer[Any]):
    uid = serializers.CharField(
        max_length=100,
    )
    token = serializers.CharField(
        max_length=100,
    )
