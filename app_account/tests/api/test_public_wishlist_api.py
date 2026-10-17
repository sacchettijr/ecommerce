from typing import Any, cast

import pytest
from django.test import Client

from app_account.models import UserModel, UserWishlistModel
from app_account.tests.factories import UserFactory, UserWishlistItemFactory
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

BASE = "/api/account/wishlist/public"


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def wishlist_of(user: UserModel) -> UserWishlistModel:
    return UserWishlistModel.objects.get(user=user)


def public_id_of(user: UserModel) -> str:
    return str(cast(Any, wishlist_of(user)).public_id)


def add(user: UserModel, **kwargs: Any) -> None:
    UserWishlistItemFactory(wishlist=wishlist_of(user), product=ProductFactory(), **kwargs)


def ids(response_json: dict[str, Any]) -> list[int]:
    return [row["id"] for row in response_json["items"]]


def test_public_wishlist_works_without_authentication(client: Client) -> None:
    user = make_user()
    add(user, private=False)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    assert response.status_code == 200


def test_public_wishlist_returns_only_public_items(client: Client) -> None:
    user = make_user()
    add(user, private=False)
    add(user, private=True)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    body = response.json()
    assert len(body["items"]) == 1
    for row in body["items"]:
        assert row.get("private") is None


def test_public_wishlist_response_never_contains_a_private_key(client: Client) -> None:
    user = make_user()
    add(user, private=False)
    add(user, private=True)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    for row in response.json()["items"]:
        assert "private" not in row


def test_public_wishlist_includes_the_nested_product(client: Client) -> None:
    user = make_user()
    add(user, private=False)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    row = response.json()["items"][0]
    assert row["product"]["id"]
    assert row["product"]["name"]
    assert "price" in row["product"]


def test_public_wishlist_with_only_private_items_is_an_empty_list(client: Client) -> None:
    user = make_user()
    add(user, private=True)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    assert response.json()["items"] == []


def test_unknown_public_id_is_not_found(client: Client) -> None:
    response = client.get(f"{BASE}/00000000-0000-0000-0000-000000000000/")

    assert response.status_code == 404


def test_malformed_public_id_is_not_found(client: Client) -> None:
    response = client.get(f"{BASE}/not-a-uuid/")

    assert response.status_code == 404


def test_one_users_items_never_appear_under_another_users_public_id(client: Client) -> None:
    user = make_user()
    other = make_user()
    add(other, private=False)

    response = client.get(f"{BASE}/{public_id_of(user)}/")

    assert response.json()["items"] == []
