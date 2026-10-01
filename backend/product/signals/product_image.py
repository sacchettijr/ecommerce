from typing import (
    Any,
    cast,
)

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_delete
from django.dispatch import receiver

from product.models import (
    ProductImageModel,
    ProductModel,
)
from product.models.organize_product_images import organize_product_images


@receiver(post_delete, sender=ProductImageModel)
def reorganize_product_images_after_delete(
    sender: type[ProductImageModel],
    instance: ProductImageModel,
    origin: Any,
    **kwargs: Any,
) -> None:

    origin_model = cast(Any, origin).model if isinstance(origin, QuerySet) else type(origin)

    if origin_model is not ProductImageModel:
        return

    product_id: int = cast(Any, instance).product_id

    with transaction.atomic():
        if not ProductModel.objects.select_for_update().filter(pk=product_id).exists():
            return

        images = ProductImageModel.objects.filter(product_id=product_id)
        organize_product_images(images)

        if cast(bool, instance.is_primary) and not images.filter(is_primary=True).exists():
            images.filter(order=0).update(is_primary=True)
