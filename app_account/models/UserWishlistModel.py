from typing import cast
from uuid import uuid4

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
    #   Opaque handle for the "view a third party's wishlist" public URL. Deliberately not the
    #   numeric user id (would let anyone enumerate accounts) and not a name-derived slug (no
    #   generation/collision logic, no name exposure) — see domain.md.
    public_id = models.UUIDField(
        verbose_name=_(
            message="Public ID",
        ),
        default=uuid4,
        unique=True,
        editable=False,
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
