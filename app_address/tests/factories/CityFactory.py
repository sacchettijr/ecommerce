from typing import TYPE_CHECKING

from factory.declarations import SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from app_address.models import CityModel
from app_address.tests.factories.StateFactory import StateFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[CityModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class CityFactory(BaseDjangoModelFactory):
    name = Faker(
        provider="city",
        locale="pt-br",
    )
    state = SubFactory(
        factory=StateFactory,
    )

    class Meta:
        model = CityModel
