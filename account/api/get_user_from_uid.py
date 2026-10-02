from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from account.models import UserModel


def get_user_from_uid(
    uid: str,
) -> UserModel | None:
    try:
        pk = force_str(
            s=urlsafe_base64_decode(
                s=uid,
            ),
        )

        return UserModel.objects.get(
            pk=pk,
        )
    except (
        TypeError,
        ValueError,
        OverflowError,
        ValidationError,
        UserModel.DoesNotExist,
    ):
        return None
