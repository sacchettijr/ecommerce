from typing import TYPE_CHECKING

from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from app_account.models import UserWishlistModel
from app_account.tests.factories.UserFactory import UserFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[UserWishlistModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class UserWishlistFactory(BaseDjangoModelFactory):
    user = SubFactory(
        factory=UserFactory,
    )

    class Meta:
        model = UserWishlistModel
        django_get_or_create = ("user",)
