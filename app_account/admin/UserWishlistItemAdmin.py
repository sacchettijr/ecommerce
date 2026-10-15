from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from app_account.forms import (
    UserWishlistItemCreateForm,
    UserWishlistItemUpdateForm,
)
from app_account.models import UserWishlistItemModel

if TYPE_CHECKING:
    BaseUserWishlistItemAdmin = admin.ModelAdmin[UserWishlistItemModel]
else:
    BaseUserWishlistItemAdmin = admin.ModelAdmin


@admin.register(UserWishlistItemModel)
class UserWishlistItemAdmin(BaseUserWishlistItemAdmin):
    list_display = (
        "id",
        "wishlist",
        "product",
        "position",
        "added_at",
    )
    list_filter = (
        "wishlist",
        "product",
        "added_at",
    )
    search_fields = (
        "wishlist__user__email",
        "wishlist__user__name",
        "product__name",
    )

    autocomplete_fields = ("product",)

    add_form = UserWishlistItemCreateForm
    form = UserWishlistItemUpdateForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[UserWishlistItemModel]:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "wishlist__user",
                "product",
            )
        )
