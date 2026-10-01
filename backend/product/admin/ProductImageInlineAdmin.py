from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils.translation import (
    gettext_lazy as _,
)

from product.forms import ProductImageForm
from product.models import (
    ProductImageModel,
    ProductModel,
)
from utils.image import image_preview

if TYPE_CHECKING:
    BaseProductImageAdmin = admin.TabularInline[
        ProductImageModel,
        ProductModel,
    ]
else:
    BaseProductImageAdmin = admin.TabularInline


class ProductImageInlineAdmin(BaseProductImageAdmin):
    model = ProductImageModel
    form = ProductImageForm
    extra = 1
    fields = (
        "image",
        "image_preview",
        "is_primary",
        "order",
    )
    readonly_fields = ("image_preview",)

    @admin.display(
        description=_(
            message="Preview",
        ),
    )
    def image_preview(
        self,
        obj: ProductImageModel,
    ) -> str:
        return image_preview(
            obj.image,
        )
