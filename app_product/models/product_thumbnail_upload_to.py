from typing import Protocol

from utils.upload import generate_upload_path


class ProductThumbnailInstance(Protocol):
    @property
    def pk(self) -> int | None: ...


def product_thumbnail_upload_to(
    instance: ProductThumbnailInstance,
    filename: str,
) -> str:

    if instance.pk is None:
        raise ValueError(
            "The product must be saved before its thumbnail, which is stored under the product id."
        )

    return generate_upload_path(
        filename=filename,
        directory="products/thumbnails",
        identifier=instance.pk,
    )
