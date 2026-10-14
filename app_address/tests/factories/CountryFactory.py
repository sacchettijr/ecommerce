from typing import TYPE_CHECKING

from factory.declarations import Sequence
from factory.django import DjangoModelFactory
from factory.faker import Faker

from app_address.models import CountryModel

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[CountryModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


def generate_iso_code(number: int) -> str:
    return chr(65 + number // 26) + chr(65 + number % 26)


class CountryFactory(BaseDjangoModelFactory):
    name = Faker(
        provider="country",
        locale="pt-br",
    )
    iso_code = Sequence(
        function=generate_iso_code,
    )

    class Meta:
        model = CountryModel
