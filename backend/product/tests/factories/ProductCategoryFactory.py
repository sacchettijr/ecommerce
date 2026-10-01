from typing import TYPE_CHECKING

from factory.django import DjangoModelFactory
from factory.faker import Faker

from product.models import ProductCategoryModel

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[ProductCategoryModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class ProductCategoryFactory(BaseDjangoModelFactory):
    active = True
    name = Faker(
        provider="word",
        locale="pt-br",
    )

    class Meta:
        model = ProductCategoryModel
