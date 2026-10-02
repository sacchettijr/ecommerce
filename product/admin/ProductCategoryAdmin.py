from typing import TYPE_CHECKING

from django.contrib import admin

from product.forms import ProductCategoryForm
from product.models import ProductCategoryModel

if TYPE_CHECKING:
    BaseProductCategoryAdmin = admin.ModelAdmin[ProductCategoryModel]
else:
    BaseProductCategoryAdmin = admin.ModelAdmin


@admin.register(ProductCategoryModel)
class ProductCategoryAdmin(BaseProductCategoryAdmin):
    form = ProductCategoryForm

    list_display = (
        "id",
        "active",
        "name",
        "slug",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "active",
        "created_at",
        "updated_at",
    )

    readonly_fields = ("slug",)

    class Media:
        js = (
            "src/js/slugify.js",
            "src/js/admin/product_slug_preview.js",
        )
