from typing import TYPE_CHECKING

from django.contrib import admin

from product.forms import ProductForm
from product.models import ProductModel

from .ProductImageInlineAdmin import ProductImageInlineAdmin

if TYPE_CHECKING:
    BaseProductAdmin = admin.ModelAdmin[ProductModel]
else:
    BaseProductAdmin = admin.ModelAdmin


@admin.register(ProductModel)
class ProductAdmin(BaseProductAdmin):
    form = ProductForm

    list_display = (
        "id",
        "active",
        "name",
        "slug",
        "category",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "slug",
        "category__name",
    )

    list_filter = (
        "active",
        "created_at",
        "updated_at",
    )

    readonly_fields = ("slug",)

    inlines = (ProductImageInlineAdmin,)

    class Media:
        js = (
            "src/js/slugify.js",
            "src/js/admin/product_slug_preview.js",
        )
