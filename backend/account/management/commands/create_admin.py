from typing import Any

from django.core.management.base import BaseCommand

from account.models import UserModel
from utils.env import env


class Command(BaseCommand):
    help = 'Create a superuser from the "DJANGO_SUPERUSER_*" environment variables.'

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        email: str = env(
            name="DJANGO_SUPERUSER_EMAIL",
        )
        password: str = env(
            name="DJANGO_SUPERUSER_PASSWORD",
        )
        name: str = env(
            name="DJANGO_SUPERUSER_NAME",
        )
        date_birth: str = env(
            name="DJANGO_SUPERUSER_DATE_BIRTH",
        )

        if UserModel.objects.filter(email__iexact=email).exists():
            self.stdout.write(
                msg=f"Administrador '{email}' já existe.",
            )
            return

        UserModel.objects.create_superuser(
            email=email,
            password=password,
            name=name,
            date_birth=date_birth,
        )
        self.stdout.write(
            msg=self.style.SUCCESS(
                text=f"Administrador '{email}' criado com sucesso.",
            ),
        )
