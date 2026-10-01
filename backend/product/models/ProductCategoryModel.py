from typing import cast

from django.conf import settings
from django.utils.translation import (
    gettext_lazy as _,
)

from product.models.ProductBaseModel import ProductBaseModel


class ProductCategoryModel(ProductBaseModel):
    class Meta(ProductBaseModel.Meta):
        db_table = "product_category"
        verbose_name = _(
            message="Category",
        )
        verbose_name_plural = _(
            message="Categories",
        )

    def get_absolute_url(self) -> str:
        slug = cast(
            str,
            self.slug,
        )
        return f"{settings.FRONTEND_URL}/categories/{slug}"
