from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(
    AppConfig,
):
    name = "account"
    verbose_name = _(
        message="Account",
    )

    def ready(
        self,
    ) -> None:
        from django.db.models.signals import post_migrate

        from account.signals import create_default_superuser

        post_migrate.connect(
            receiver=create_default_superuser,
            sender=self,
        )
        return super().ready()
