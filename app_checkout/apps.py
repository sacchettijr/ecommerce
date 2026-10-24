from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import (
    gettext_lazy as _,
)


class AppCheckoutConfig(AppConfig):
    name = "app_checkout"
    label = "checkout"
    verbose_name = _(
        message="Checkout",
    )

    def ready(self) -> None:
        import_module(
            name="app_checkout.signals.remove_product_from_carts_when_deactivated",
        )
