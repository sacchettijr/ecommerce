from collections.abc import Collection
from typing import (
    Any,
    ClassVar,
    cast,
)

from django.db import models, transaction
from django.db.models.constraints import BaseConstraint
from django.db.models.fields.related import ForeignKey
from django.utils.translation import (
    gettext_lazy as _,
)

from app_core.models import BaseModel
from app_product.models import ProductModel

from .organize_wishlist_items import organize_wishlist_items
from .UserWishlistModel import UserWishlistModel


class UserWishlistItemModel(BaseModel):
    wishlist: ForeignKey[UserWishlistModel, UserWishlistModel] = models.ForeignKey(
        to="account.UserWishlistModel",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product: ForeignKey[ProductModel, ProductModel] = models.ForeignKey(
        to="product.ProductModel",
        on_delete=models.CASCADE,
        related_name="wishlisted_by_users",
    )
    added_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(
        verbose_name=_(
            message="Position",
        ),
        default=0,
    )

    class Meta:
        db_table = "user_wishlist_item"
        verbose_name = _(
            message="User Wishlist Item",
        )
        verbose_name_plural = _(
            message="User Wishlist Items",
        )
        ordering = (
            "wishlist",
            "position",
            "id",
        )
        constraints: ClassVar[list[BaseConstraint]] = [
            models.UniqueConstraint(
                fields=[
                    "wishlist",
                    "product",
                ],
                name="unique_product_per_wishlist",
            ),
            models.UniqueConstraint(
                fields=[
                    "wishlist",
                    "position",
                ],
                name="unique_position_per_wishlist",
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]

    def __str__(self) -> str:
        return f"Wishlist Item: {self.product} in {self.wishlist}"

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        wishlist_id: int = cast(Any, self).wishlist_id
        is_adding = self._state.adding
        previous_wishlist_id = (
            None
            if is_adding
            else (
                type(self)
                .objects.filter(
                    pk=self.pk,
                )
                .values_list(
                    "wishlist_id",
                    flat=True,
                )
                .first()
            )
        )

        with transaction.atomic():
            UserWishlistModel.objects.select_for_update().only("pk").get(
                pk=wishlist_id,
            )

            siblings = type(self).objects.filter(
                wishlist_id=wishlist_id,
            )

            if is_adding:
                self.position = siblings.count()

            super().save(*args, **kwargs)
            organize_wishlist_items(
                items=siblings,
                anchor=self,
            )

            if previous_wishlist_id is not None and previous_wishlist_id != wishlist_id:
                organize_wishlist_items(
                    type(self).objects.filter(
                        wishlist_id=previous_wishlist_id,
                    ),
                )

    def validate_constraints(
        self,
        exclude: Collection[str] | None = None,
    ) -> None:
        super().validate_constraints(exclude={*(exclude or ()), "position"})

    def _get_unique_checks(
        self,
        exclude: Collection[str] | None = None,
        include_meta_constraints: bool = False,
    ) -> tuple[list[Any], list[Any]]:
        unique_checks, date_checks = cast(Any, super())._get_unique_checks(
            exclude=exclude,
            include_meta_constraints=include_meta_constraints,
        )

        return (
            [
                check
                for check in unique_checks
                if set(check[1])
                != {
                    "wishlist",
                    "position",
                }
            ],
            date_checks,
        )
