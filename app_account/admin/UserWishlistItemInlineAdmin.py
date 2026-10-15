from typing import TYPE_CHECKING

from django.contrib import admin

from app_account.forms import UserWishlistItemBaseForm
from app_account.models import (
    UserWishlistItemModel,
    UserWishlistModel,
)

if TYPE_CHECKING:
    BaseUserWishlistItemInlineAdmin = admin.TabularInline[
        UserWishlistItemModel,
        UserWishlistModel,
    ]
else:
    BaseUserWishlistItemInlineAdmin = admin.TabularInline


class UserWishlistItemInlineAdmin(BaseUserWishlistItemInlineAdmin):
    model = UserWishlistItemModel
    form = UserWishlistItemBaseForm
    fk_name = "wishlist"
    extra = 1
    autocomplete_fields = ("product",)

    fields = (
        "product",
        "position",
        "added_at",
    )
    readonly_fields = (
        "position",
        "added_at",
    )
