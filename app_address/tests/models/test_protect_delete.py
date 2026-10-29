from typing import Any, cast

import pytest
from django.db.models import ProtectedError

from app_account.tests.factories import UserAddressFactory
from app_address.models import CityModel, CountryModel, StateModel
from app_address.tests.factories import CityFactory, CountryFactory, StateFactory

pytestmark = pytest.mark.django_db


# -------------------------------------------------- geography hierarchy (PROTECT)


def test_a_country_with_states_cannot_be_deleted() -> None:
    state = cast(Any, StateFactory())
    country = cast(CountryModel, state.country)

    with pytest.raises(ProtectedError):
        country.delete()
    assert CountryModel.objects.filter(pk=country.pk).exists()


def test_a_country_without_states_can_be_deleted() -> None:
    country = cast(CountryModel, CountryFactory())

    country.delete()

    assert not CountryModel.objects.filter(pk=country.pk).exists()


def test_a_state_with_cities_cannot_be_deleted() -> None:
    city = cast(Any, CityFactory())
    state = cast(StateModel, city.state)

    with pytest.raises(ProtectedError):
        state.delete()
    assert StateModel.objects.filter(pk=state.pk).exists()


def test_a_state_without_cities_can_be_deleted() -> None:
    state = cast(StateModel, StateFactory())

    state.delete()

    assert not StateModel.objects.filter(pk=state.pk).exists()


# ------------------------------------------- referenced by a user address (PROTECT)


def test_a_city_referenced_by_a_user_address_cannot_be_deleted() -> None:
    address = cast(Any, UserAddressFactory())
    city = cast(CityModel, address.city)

    with pytest.raises(ProtectedError):
        city.delete()
    assert CityModel.objects.filter(pk=city.pk).exists()


def test_a_state_referenced_by_a_user_address_cannot_be_deleted() -> None:
    address = cast(Any, UserAddressFactory())
    state = cast(StateModel, address.state)

    with pytest.raises(ProtectedError):
        state.delete()
    assert StateModel.objects.filter(pk=state.pk).exists()


def test_a_country_referenced_by_a_user_address_cannot_be_deleted() -> None:
    address = cast(Any, UserAddressFactory())
    country = cast(CountryModel, address.country)

    with pytest.raises(ProtectedError):
        country.delete()
    assert CountryModel.objects.filter(pk=country.pk).exists()


# ------------------------------------ documented finding: no uniqueness constraint
#
#   Confirmed by direct inspection of CountryModel/StateModel/CityModel/migrations:
#   none of the three has any uniqueness constraint (no unique_together, no
#   UniqueConstraint, no field-level unique=True) on name/code within their parent.
#   This is a genuine data-integrity gap worth the user's attention, but adding a
#   constraint is a production-behavior change outside this testing task's scope —
#   see the final report. These tests document today's actual (unconstrained)
#   behavior as a regression guard, not as an endorsement of it.


def test_two_states_with_the_same_name_in_the_same_country_are_currently_allowed() -> None:
    country = cast(CountryModel, CountryFactory())

    first = cast(Any, StateFactory(country=country, name="Duplicate State"))
    second = cast(Any, StateFactory(country=country, name="Duplicate State"))

    assert first.pk != second.pk
    assert StateModel.objects.filter(country=country, name="Duplicate State").count() == 2


def test_two_cities_with_the_same_name_in_the_same_state_are_currently_allowed() -> None:
    state = cast(StateModel, StateFactory())

    first = cast(Any, CityFactory(state=state, name="Duplicate City"))
    second = cast(Any, CityFactory(state=state, name="Duplicate City"))

    assert first.pk != second.pk
    assert CityModel.objects.filter(state=state, name="Duplicate City").count() == 2
