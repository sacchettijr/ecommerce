from typing import TYPE_CHECKING

from django.contrib import admin

from app_checkout.forms import (
    CartItemCreateForm,
    CartItemUpdateForm,
)
from app_checkout.models import CartItemModel

if TYPE_CHECKING:
    BaseCartItemAdmin = admin.ModelAdmin[CartItemModel]
else:
    BaseCartItemAdmin = admin.ModelAdmin


@admin.register(CartItemModel)
class CartItemAdmin(BaseCartItemAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "price",
    )
    list_display_links = (
        "id",
        "user",
    )
    list_filter = ("user",)
    search_fields = (
        "user__email",
        "user__name",
    )
    add_form = CartItemCreateForm
    form = CartItemUpdateForm
