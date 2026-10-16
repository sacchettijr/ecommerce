from typing import Any, cast

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app_account.models import UserAddressModel


@receiver(post_delete, sender=UserAddressModel)
def promote_primary_address_after_delete(
    sender: type[UserAddressModel],
    instance: UserAddressModel,
    origin: Any,
    **kwargs: Any,
) -> None:
    #   Mirrors ProductImageModel's post_delete signal: if the address that was just deleted
    #   was the user's primary one and other addresses remain, promote one of them so the
    #   "has addresses => exactly one primary" invariant keeps holding. Addresses have no
    #   explicit order, so the oldest remaining one is promoted deterministically.
    origin_model = cast(Any, origin).model if isinstance(origin, QuerySet) else type(origin)

    if origin_model is not UserAddressModel:
        return

    user_id: int = cast(Any, instance).user_id

    with transaction.atomic():
        if not get_user_model().objects.select_for_update().filter(pk=user_id).exists():
            #   The user itself was deleted (cascading to this address too) — nothing to do.
            return

        addresses = UserAddressModel.objects.filter(user_id=user_id)

        #   Checking the invariant directly ("addresses remain but none is primary")
        #   rather than trusting instance.primary: when a ModelForm deletes a row (admin
        #   inline formset), Django binds the submitted field data onto form.instance
        #   before deleting it, so instance.primary can reflect an unchecked/omitted
        #   checkbox rather than the address's actual last-known state in the database
        #   (same bug confirmed and fixed in app_product.signals.product_image).
        if addresses.exists() and not addresses.filter(primary=True).exists():
            first = addresses.order_by("created_at").first()
            if first is not None:
                addresses.filter(pk=first.pk).update(primary=True)
