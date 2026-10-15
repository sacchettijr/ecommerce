from typing import TYPE_CHECKING

from factory.declarations import SubFactory
from factory.django import DjangoModelFactory

from app_account.models import UserWishlistItemModel
from app_account.tests.factories.UserWishlistFactory import UserWishlistFactory
from app_product.tests.factories import ProductFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[UserWishlistItemModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class UserWishlistItemFactory(BaseDjangoModelFactory):
    wishlist = SubFactory(
        factory=UserWishlistFactory,
    )
    product = SubFactory(
        factory=ProductFactory,
    )

    class Meta:
        model = UserWishlistItemModel
