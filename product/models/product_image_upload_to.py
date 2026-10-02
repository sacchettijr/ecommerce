from typing import Protocol

from utils.upload import generate_upload_path


class ProductImageInstance(Protocol):
    product_id: int


def product_image_upload_to(
    instance: ProductImageInstance,
    filename: str,
) -> str:

    return generate_upload_path(
        filename=filename,
        directory="products",
        identifier=instance.product_id,
    )
