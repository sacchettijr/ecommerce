from typing import (
    TYPE_CHECKING,
    cast,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .UserWishlistItemModel import UserWishlistItemModel


def _position(item: UserWishlistItemModel) -> int:
    return cast(int, item.position)


def organize_wishlist_items(
    items: QuerySet[UserWishlistItemModel],
    anchor: UserWishlistItemModel | None = None,
) -> None:
    ordered = list(
        items.exclude(
            pk=anchor.pk,
        )
        if anchor is not None
        else items
    )

    if anchor is not None:
        position = next(
            (
                index
                for index, item in enumerate(ordered)
                if _position(item)
                >= _position(
                    item=anchor,
                )
            ),
            len(ordered),
        )
        ordered.insert(position, anchor)

    changed: list[UserWishlistItemModel] = []

    for position, item in enumerate(ordered):
        if _position(item) != position:
            item.position = position
            changed.append(item)

    if changed:
        items.bulk_update(
            changed,
            fields=[
                "position",
            ],
        )
