from typing import TYPE_CHECKING

from factory.declarations import SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from app_account.models import UserAddressModel
from app_account.tests.factories.UserFactory import UserFactory
from app_address.tests.factories import CityFactory, CountryFactory, StateFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[UserAddressModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class UserAddressFactory(BaseDjangoModelFactory):
    user = SubFactory(
        factory=UserFactory,
    )
    street = Faker(
        provider="street_name",
        locale="pt-br",
    )
    number = Faker(
        provider="building_number",
        locale="pt-br",
    )
    district = Faker(
        provider="bairro",
        locale="pt-br",
    )
    postal_code = Faker(
        provider="postcode",
        locale="pt-br",
    )
    city = SubFactory(
        factory=CityFactory,
    )
    state = SubFactory(
        factory=StateFactory,
    )
    country = SubFactory(
        factory=CountryFactory,
    )

    class Meta:
        model = UserAddressModel
