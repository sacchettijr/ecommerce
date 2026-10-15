from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from app_account.models import UserModel, UserWishlistModel


@receiver(post_save, sender=UserModel)
def create_wishlist_for_new_user(
    sender: type[UserModel],
    instance: UserModel,
    created: bool,
    **kwargs: Any,
) -> None:
    if not created:
        return

    UserWishlistModel.objects.get_or_create(
        user=instance,
    )
