from typing import TYPE_CHECKING, Any, cast

from factory.declarations import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from app_account.models import UserAddressModel
from app_account.tests.factories.UserFactory import UserFactory
from app_address.models import CountryModel, StateModel
from app_address.tests.factories import CityFactory

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[UserAddressModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


def state_of_city(address: UserAddressModel) -> StateModel:
    return cast(StateModel, cast(Any, address).city.state)


def country_of_city(address: UserAddressModel) -> CountryModel:
    return cast(CountryModel, cast(Any, address).city.state.country)


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
    #   Derived from city, not an independent SubFactory - a UserAddressModel's
    #   country/state/city must agree with each other (enforced server-side by
    #   UserAddressBaseForm.clean()), so the factory's own output should too.
    state = LazyAttribute(
        function=state_of_city,
    )
    country = LazyAttribute(
        function=country_of_city,
    )

    class Meta:
        model = UserAddressModel
