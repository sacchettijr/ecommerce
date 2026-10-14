from rest_framework import serializers

from app_account.models import UserModel


class UserSerializer(serializers.ModelSerializer[UserModel]):
    class Meta:
        model = UserModel
        fields = (
            "id",
            "name",
            "email",
            "date_birth",
            "phone",
            "created_at",
            "is_staff",
        )
        read_only_fields = fields
