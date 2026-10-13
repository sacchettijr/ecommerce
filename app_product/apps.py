from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import (
    gettext_lazy as _,
)


class ProductConfig(AppConfig):
    name = "app_product"
    label = "product"
    verbose_name = _(
        message="Product",
    )

    def ready(self) -> None:
        import_module(name="app_product.signals.product_image")
