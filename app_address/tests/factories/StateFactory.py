from typing import TYPE_CHECKING

from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from app_address.models import StateModel
from app_address.tests.factories.CountryFactory import CountryFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[StateModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


def generate_state_code(number: int) -> str:
    return chr(65 + number // 26) + chr(65 + number % 26)


class StateFactory(BaseDjangoModelFactory):
    name = Faker(
        provider="state",
        locale="pt-br",
    )
    code = Sequence(
        function=generate_state_code,
    )
    country = SubFactory(
        factory=CountryFactory,
    )

    class Meta:
        model = StateModel
