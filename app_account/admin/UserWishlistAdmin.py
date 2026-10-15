from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from app_account.forms import (
    UserWishlistCreateForm,
    UserWishlistUpdateForm,
)
from app_account.models import UserWishlistModel

from .UserWishlistItemInlineAdmin import UserWishlistItemInlineAdmin

if TYPE_CHECKING:
    BaseUserWishlistAdmin = admin.ModelAdmin[UserWishlistModel]
else:
    BaseUserWishlistAdmin = admin.ModelAdmin


@admin.register(UserWishlistModel)
class UserWishlistAdmin(BaseUserWishlistAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__email",
        "user__name",
    )

    add_form = UserWishlistCreateForm
    form = UserWishlistUpdateForm

    inlines = (UserWishlistItemInlineAdmin,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[UserWishlistModel]:
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related(
                "items__product",
            )
        )
