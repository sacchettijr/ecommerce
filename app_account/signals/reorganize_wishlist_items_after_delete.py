from typing import Any, cast

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app_account.models import (
    UserWishlistItemModel,
    UserWishlistModel,
)
from app_account.models.organize_wishlist_items import (
    organize_wishlist_items,
)


@receiver(post_delete, sender=UserWishlistItemModel)
def reorganize_wishlist_items_after_delete(
    sender: type[UserWishlistItemModel],
    instance: UserWishlistItemModel,
    origin: Any,
    **kwargs: Any,
) -> None:
    origin_model = (
        cast(
            Any,
            origin,
        ).model
        if isinstance(
            origin,
            QuerySet,
        )
        else type(origin)
    )

    if origin_model is not UserWishlistItemModel:
        return

    wishlist_id: int = cast(Any, instance).wishlist_id

    with transaction.atomic():
        if (
            not UserWishlistModel.objects.select_for_update()
            .filter(
                pk=wishlist_id,
            )
            .exists()
        ):
            #   The wishlist itself was deleted (cascading to this item too) — nothing to do.
            return

        items = UserWishlistItemModel.objects.filter(
            wishlist_id=wishlist_id,
        )
        organize_wishlist_items(items)
