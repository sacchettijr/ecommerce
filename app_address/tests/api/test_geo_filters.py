from typing import cast

import pytest
from django.test import Client

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_address.models import CityModel, CountryModel, StateModel
from app_address.tests.factories import CityFactory, CountryFactory, StateFactory

pytestmark = pytest.mark.django_db


def make_staff_client() -> Client:
    client = Client()
    user = cast(UserModel, UserFactory(is_staff=True, is_superuser=True))
    client.force_login(user)
    return client


def make_geo() -> tuple[CountryModel, CountryModel, StateModel, StateModel]:
    country_1 = cast(CountryModel, CountryFactory())
    country_2 = cast(CountryModel, CountryFactory())
    state_1 = cast(StateModel, StateFactory(country=country_1))
    state_2 = cast(StateModel, StateFactory(country=country_2))
    return country_1, country_2, state_1, state_2


# ---------------------------------------------------------- states


def test_states_filtered_by_country() -> None:
    country_1, _, state_1, state_2 = make_geo()
    client = make_staff_client()

    response = client.get(f"/api/address/states/?country={country_1.pk}")

    assert response.status_code == 200
    ids = {row["id"] for row in response.json()}
    assert ids == {state_1.pk}
    assert state_2.pk not in ids


def test_states_without_a_country_filter_returns_everything() -> None:
    _, _, state_1, state_2 = make_geo()
    client = make_staff_client()

    response = client.get("/api/address/states/")

    ids = {row["id"] for row in response.json()}
    assert {state_1.pk, state_2.pk} <= ids


def test_states_endpoint_rejects_anonymous_access() -> None:
    country, _, _, _ = make_geo()

    response = Client().get(f"/api/address/states/?country={country.pk}")

    assert response.status_code in (401, 403)


def test_states_endpoint_rejects_a_non_staff_authenticated_user() -> None:
    country, _, _, _ = make_geo()
    client = Client()
    client.force_login(cast(UserModel, UserFactory(is_staff=False)))

    response = client.get(f"/api/address/states/?country={country.pk}")

    assert response.status_code == 403


# ---------------------------------------------------------- cities


def test_cities_filtered_by_state() -> None:
    _, _, state_1, state_2 = make_geo()
    city_1 = cast(CityModel, CityFactory(state=state_1))
    CityFactory(state=state_2)
    client = make_staff_client()

    response = client.get(f"/api/address/cities/?state={state_1.pk}")

    ids = {row["id"] for row in response.json()}
    assert ids == {city_1.pk}


def test_cities_endpoint_rejects_anonymous_access() -> None:
    _, _, state, _ = make_geo()

    response = Client().get(f"/api/address/cities/?state={state.pk}")

    assert response.status_code in (401, 403)
