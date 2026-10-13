from typing import Any

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from utils.normalize import (
    normalize_email,
    normalize_whitespace,
)
from utils.validator import (
    validate_name,
)


class ContactSerializer(serializers.Serializer[Any]):
    name = serializers.CharField(
        min_length=3,
        max_length=255,
        validators=[
            validate_name,
        ],
    )
    email = serializers.EmailField()
    phone = PhoneNumberField(
        region="BR",
    )
    message = serializers.CharField(
        min_length=10,
        max_length=2000,
    )

    def validate_name(
        self,
        value: str,
    ) -> str:
        return normalize_whitespace(
            name=value,
        )

    def validate_email(
        self,
        value: str,
    ) -> str:
        return normalize_email(
            email=value,
        )

    def validate_message(
        self,
        value: str,
    ) -> str:
        return " ".join(
            value.split(),
        )
