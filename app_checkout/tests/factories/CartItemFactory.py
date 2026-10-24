from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    cast,
)

from factory.declarations import (
    LazyAttribute,
    SubFactory,
)
from factory.django import DjangoModelFactory

from app_account.tests.factories import UserFactory
from app_checkout.models import CartItemModel
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[CartItemModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


def price_of_product(
    cart_item: CartItemModel,
) -> Decimal:
    return cast(
        Decimal,
        cast(
            ProductModel,
            cart_item.product,
        ).price,
    )


class CartItemFactory(BaseDjangoModelFactory):
    user = SubFactory(factory=UserFactory)
    product = SubFactory(factory=ProductFactory)
    quantity = 1

    price = LazyAttribute(function=price_of_product)

    class Meta:
        model = CartItemModel
