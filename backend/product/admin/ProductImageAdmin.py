from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils.translation import (
    gettext_lazy as _,
)

from product.forms import ProductImageForm
from product.models import ProductImageModel
from utils.image import image_preview

if TYPE_CHECKING:
    BaseProductImageAdmin = admin.ModelAdmin[ProductImageModel]
else:
    BaseProductImageAdmin = admin.ModelAdmin


@admin.register(ProductImageModel)
class ProductImageAdmin(BaseProductImageAdmin):
    form = ProductImageForm

    list_display = (
        "id",
        "product",
        "image_preview",
        "is_primary",
        "order",
        "created_at",
    )

    list_display_links = (
        "id",
        "product",
    )

    search_fields = ("product__name",)

    list_filter = (
        "is_primary",
        "created_at",
    )

    ordering = (
        "product",
        "order",
    )

    readonly_fields = ("image_preview",)

    @admin.display(
        description=_(
            message="Preview",
        )
    )
    def image_preview(
        self,
        obj: ProductImageModel,
    ) -> str:
        return image_preview(
            image=obj.image,
        )
