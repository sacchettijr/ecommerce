from rest_framework import serializers

from account.models import UserModel


class UserSerializer(serializers.ModelSerializer[UserModel]):
    class Meta:
        model = UserModel
        fields = (
            "id",
            "name",
            "email",
            "is_staff",
        )
        read_only_fields = fields
