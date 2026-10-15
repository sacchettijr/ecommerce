from typing import cast

from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)

from app_core.models import BaseModel

from .UserModel import UserModel


class UserWishlistModel(BaseModel):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_wishlist",
    )

    class Meta:
        db_table = "user_wishlist"
        verbose_name = _(
            message="User Wishlist",
        )
        verbose_name_plural = _(
            message="User Wishlists",
        )

    def __str__(self) -> str:
        user = cast(
            UserModel,
            self.user,
        )
        return f"User Wishlist: {user}"
