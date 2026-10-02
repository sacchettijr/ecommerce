from typing import (
    TYPE_CHECKING,
    cast,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .ProductImageModel import ProductImageModel


def _order(image: ProductImageModel) -> int:
    return cast(int, image.order)


def organize_product_images(
    images: QuerySet[ProductImageModel],
    anchor: ProductImageModel | None = None,
) -> None:
    ordered = list(images.exclude(pk=anchor.pk) if anchor is not None else images)

    if anchor is not None:
        position = next(
            (index for index, image in enumerate(ordered) if _order(image) >= _order(anchor)),
            len(ordered),
        )
        ordered.insert(position, anchor)

    changed: list[ProductImageModel] = []

    for position, image in enumerate(ordered):
        if _order(image) != position:
            image.order = position
            changed.append(image)

    if changed:
        images.bulk_update(changed, fields=["order"])
