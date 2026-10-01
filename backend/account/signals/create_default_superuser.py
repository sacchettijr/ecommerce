from typing import (
    Any,
)

from django.apps import (
    AppConfig,
)

from account.models import (
    UserModel,
)
from utils.env import (
    env,
)


def create_default_superuser(
    sender: AppConfig,
    **kwargs: Any,
) -> None:

    if UserModel.objects.filter(is_superuser=True).exists():
        return

    email = env(
        name="DJANGO_SUPERUSER_EMAIL",
        default="admin@example.com",
    )
    password = env(
        name="DJANGO_SUPERUSER_PASSWORD",
        default="admin123",
    )
    name = env(
        name="DJANGO_SUPERUSER_NAME",
        default="Administrador",
    )
    date_birth = env(
        name="DJANGO_SUPERUSER_DATE_BIRTH",
        default="2000-01-01",
    )

    UserModel.objects.create_superuser(
        email=email,
        password=password,
        name=name,
        date_birth=date_birth,
    )

    print(f"Default superuser created: {email}")
