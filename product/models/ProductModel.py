from typing import (
    Any,
    cast,
)

from django.conf import settings
from django.db import (
    models,
    transaction,
)
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.validator import (
    validate_positive_decimal,
)

from .product_thumbnail_upload_to import product_thumbnail_upload_to
from .ProductBaseModel import ProductBaseModel
from .ProductCategoryModel import ProductCategoryModel


class ProductModel(ProductBaseModel):
    category = models.ForeignKey(
        to=ProductCategoryModel,
        verbose_name=_(message="Category"),
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        verbose_name=_(
            message="Description",
        ),
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        verbose_name=_(
            message="Price",
        ),
        decimal_places=2,
        max_digits=10,
        validators=[
            validate_positive_decimal,
        ],
    )
    thumbnail = models.ImageField(
        verbose_name=_(
            message="Thumbnail",
        ),
        upload_to=product_thumbnail_upload_to,
        blank=True,
        null=True,
    )

    class Meta(ProductBaseModel.Meta):
        db_table = "product"
        verbose_name = _(message="Product")
        verbose_name_plural = _(message="Products")

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        #   O upload_to do thumbnail usa o id do produto, que só existe depois do INSERT:
        #   num produto novo, o arquivo é gravado num segundo passo.
        pending = self.thumbnail if self._state.adding and self.thumbnail else None

        if pending is None:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            self.thumbnail = None
            super().save(*args, **kwargs)

            self.thumbnail = pending
            super().save(update_fields=["thumbnail"])

    def get_absolute_url(self) -> str:
        slug = cast(
            str,
            self.slug,
        )
        return f"{settings.FRONTEND_URL}/product/{slug}"
