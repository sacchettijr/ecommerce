from typing import (
    Any,
    cast,
)

from account.api.serializers import UserSerializer
from account.models import UserModel


def serialize_user(
    user: UserModel,
) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        UserSerializer(
            instance=user,
        ).data,
    )
