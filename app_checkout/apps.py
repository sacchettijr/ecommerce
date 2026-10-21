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
