from typing import Any, cast

import pytest

from app_account.forms import UserAddressBaseForm
from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_address.models import CityModel, CountryModel, StateModel
from app_address.tests.factories import CityFactory, CountryFactory, StateFactory

pytestmark = pytest.mark.django_db


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def base_data(user: UserModel, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "user": user.pk,
        "street": "Main St",
        "number": "123",
        "complement": "",
        "reference": "",
        "district": "Downtown",
        "postal_code": "00000-000",
        "primary": False,
    }
    data.update(overrides)
    return data


def test_consistent_country_state_city_is_accepted() -> None:
    country = cast(CountryModel, CountryFactory())
    state = cast(StateModel, StateFactory(country=country))
    city = cast(CityModel, CityFactory(state=state))

    form = UserAddressBaseForm(
        data=base_data(
            make_user(),
            country=country.pk,
            state=state.pk,
            city=city.pk,
        ),
    )

    assert form.is_valid(), form.errors


def test_a_state_from_a_different_country_is_rejected() -> None:
    country = cast(CountryModel, CountryFactory())
    other_country = cast(CountryModel, CountryFactory())
    state_of_other_country = cast(StateModel, StateFactory(country=other_country))
    city = cast(CityModel, CityFactory(state=cast(StateModel, StateFactory(country=country))))

    form = UserAddressBaseForm(
        data=base_data(
            make_user(),
            country=country.pk,
            state=state_of_other_country.pk,
            city=city.pk,
        ),
    )

    assert form.is_valid() is False
    assert "state" in form.errors


def test_a_city_from_a_different_state_is_rejected() -> None:
    country = cast(CountryModel, CountryFactory())
    state = cast(StateModel, StateFactory(country=country))
    other_state = cast(StateModel, StateFactory(country=country))
    city_of_other_state = cast(CityModel, CityFactory(state=other_state))

    form = UserAddressBaseForm(
        data=base_data(
            make_user(),
            country=country.pk,
            state=state.pk,
            city=city_of_other_state.pk,
        ),
    )

    assert form.is_valid() is False
    assert "city" in form.errors


def test_editing_an_existing_consistent_address_still_validates() -> None:
    country = cast(CountryModel, CountryFactory())
    state = cast(StateModel, StateFactory(country=country))
    city = cast(CityModel, CityFactory(state=state))
    user = make_user()

    create_form = UserAddressBaseForm(
        data=base_data(user, country=country.pk, state=state.pk, city=city.pk),
    )
    assert create_form.is_valid(), create_form.errors
    address = create_form.save()

    edit_form = UserAddressBaseForm(
        instance=address,
        data=base_data(
            user,
            country=country.pk,
            state=state.pk,
            city=city.pk,
            district="New District",
        ),
    )

    assert edit_form.is_valid(), edit_form.errors
