from typing import Any, cast

import pytest
from django.test import Client

from app_account.models import UserAddressModel, UserModel
from app_account.tests.factories import UserAddressFactory, UserFactory

pytestmark = pytest.mark.django_db

BASE = "/api/account/addresses"


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def add(user: UserModel, **kwargs: Any) -> UserAddressModel:
    return cast(UserAddressModel, UserAddressFactory(user=user, **kwargs))


def primary_ids(response_json: list[dict[str, Any]]) -> list[int]:
    return [row["id"] for row in response_json if row["primary"]]


# ---------------------------------------------------------- list


def test_list_requires_authentication(client: Client) -> None:
    response = client.get(f"{BASE}/")

    assert response.status_code == 403


def test_list_returns_only_the_authenticated_users_addresses(client: Client) -> None:
    user = make_user()
    other = make_user()
    mine = add(user)
    add(other)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    body = response.json()
    assert response.status_code == 200
    assert [row["id"] for row in body] == [mine.pk]


def test_list_is_an_empty_array_when_the_user_has_no_addresses(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.get(f"{BASE}/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_shows_the_primary_address_first(client: Client) -> None:
    user = make_user()
    first = add(user)
    second = add(user, primary=True)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    body = response.json()
    assert [row["id"] for row in body] == [second.pk, first.pk]


def test_list_includes_nested_city_state_and_country_names(client: Client) -> None:
    user = make_user()
    address = add(user)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    row = response.json()[0]
    assert row["id"] == address.pk
    assert row["city"]["name"]
    assert row["state"]["name"]
    assert row["country"]["name"]
    assert "password" not in row


# ---------------------------------------------------------- set-primary


def test_set_primary_requires_authentication(client: Client) -> None:
    user = make_user()
    address = add(user)

    response = client.post(f"{BASE}/{address.pk}/set-primary/")

    assert response.status_code == 403


def test_set_primary_makes_the_address_primary_and_unsets_the_others(client: Client) -> None:
    user = make_user()
    first = add(user)
    second = add(user)
    client.force_login(user)

    response = client.post(f"{BASE}/{second.pk}/set-primary/")

    body = response.json()
    first.refresh_from_db()
    second.refresh_from_db()
    assert response.status_code == 200
    assert cast(bool, second.primary) is True
    assert cast(bool, first.primary) is False
    assert primary_ids(body) == [second.pk]


def test_set_primary_returns_the_full_authoritative_address_list(client: Client) -> None:
    user = make_user()
    first = add(user)
    second = add(user)
    client.force_login(user)

    response = client.post(f"{BASE}/{second.pk}/set-primary/")

    body = response.json()
    assert {row["id"] for row in body} == {first.pk, second.pk}


def test_set_primary_on_the_already_primary_address_is_a_no_op(client: Client) -> None:
    user = make_user()
    address = add(user, primary=True)
    client.force_login(user)

    response = client.post(f"{BASE}/{address.pk}/set-primary/")

    address.refresh_from_db()
    assert response.status_code == 200
    assert cast(bool, address.primary) is True


def test_a_user_cannot_set_another_users_address_as_primary(client: Client) -> None:
    user = make_user()
    other = make_user()
    mine = add(user, primary=True)
    other_address = add(other, primary=True)
    client.force_login(user)

    response = client.post(f"{BASE}/{other_address.pk}/set-primary/")

    other_address.refresh_from_db()
    mine.refresh_from_db()
    assert response.status_code == 404
    assert cast(bool, other_address.primary) is True
    assert cast(bool, mine.primary) is True


def test_set_primary_with_a_nonexistent_address_id_is_not_found(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.post(f"{BASE}/999999/set-primary/")

    assert response.status_code == 404
