from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(
    AppConfig,
):
    name = "app_account"
    label = "account"
    verbose_name = _(
        message="Account",
    )

    def ready(
        self,
    ) -> None:
        from importlib import import_module

        from django.db.models.signals import post_migrate

        from app_account.signals import create_default_superuser

        post_migrate.connect(
            receiver=create_default_superuser,
            sender=self,
        )
        #   Connects via the @receiver decorator as a side effect of the import, same pattern
        #   as app_product's ready().
        import_module(name="app_account.signals.promote_primary_address_after_delete")
        import_module(name="app_account.signals.create_wishlist_for_new_user")
        import_module(name="app_account.signals.reorganize_wishlist_items_after_delete")

        return super().ready()
