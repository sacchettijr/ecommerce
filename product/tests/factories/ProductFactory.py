from typing import TYPE_CHECKING

from factory.declarations import SubFactory
from factory.django import (
    DjangoModelFactory,
)
from factory.faker import Faker

from product.models import ProductModel
from product.tests.factories import ProductCategoryFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[ProductModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class ProductFactory(BaseDjangoModelFactory):
    active = True
    name = Faker(
        provider="word",
        locale="pt-br",
    )
    category = SubFactory(
        factory=ProductCategoryFactory,
    )
    description = Faker(
        provider="sentence",
        locale="pt-br",
    )
    price = Faker(
        provider="pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=1,
    )

    class Meta:
        model = ProductModel
