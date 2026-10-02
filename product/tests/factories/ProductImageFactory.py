from typing import (
    TYPE_CHECKING,
)

from factory.declarations import (
    Sequence,
    SubFactory,
)
from factory.django import (
    DjangoModelFactory,
    ImageField,
)

from product.models import ProductImageModel
from product.tests.factories import ProductFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[ProductImageModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


def generate_order(number: int) -> int:
    return number


class ProductImageFactory(BaseDjangoModelFactory):
    product = SubFactory(
        factory=ProductFactory,
    )
    image = ImageField(
        filename="test.jpg",
        color="blue",
        width=10,
        height=10,
    )
    is_primary = False
    order = Sequence(
        function=generate_order,
    )

    class Meta:
        model = ProductImageModel
