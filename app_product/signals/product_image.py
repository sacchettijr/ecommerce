from typing import (
    Any,
    cast,
)

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app_product.models import (
    ProductImageModel,
    ProductModel,
)
from app_product.models.organize_product_images import organize_product_images


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

        #   Checking the invariant directly ("images remain but none is primary") rather
        #   than trusting instance.is_primary: when a ModelForm deletes a row (admin inline
        #   formset), Django binds the submitted field data onto form.instance before
        #   deleting it, so instance.is_primary can reflect an unchecked/omitted checkbox
        #   rather than the image's actual last-known state in the database.
        if images.exists() and not images.filter(is_primary=True).exists():
            #   order=0 is guaranteed unique after organize_product_images() above, but
            #   tie-break explicitly by id too, rather than relying on that implicitly.
            first = images.order_by("order", "id").first()
            if first is not None:
                images.filter(pk=first.pk).update(is_primary=True)
