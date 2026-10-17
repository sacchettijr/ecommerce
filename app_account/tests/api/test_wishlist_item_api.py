from typing import Any, cast

import pytest
from django.test import Client

from app_account.models import UserModel, UserWishlistItemModel, UserWishlistModel
from app_account.tests.factories import UserFactory, UserWishlistItemFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

BASE = "/api/account/wishlist"


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def make_product(**kwargs: Any) -> ProductModel:
    return cast(ProductModel, ProductFactory(**kwargs))


def wishlist_of(user: UserModel) -> UserWishlistModel:
    return UserWishlistModel.objects.get(user=user)


def public_id_of(user: UserModel) -> str:
    return str(cast(Any, wishlist_of(user)).public_id)


def add(user: UserModel, **kwargs: Any) -> UserWishlistItemModel:
    return cast(
        UserWishlistItemModel,
        UserWishlistItemFactory(wishlist=wishlist_of(user), **kwargs),
    )


def ids(response_json: list[dict[str, Any]]) -> list[int]:
    return [row["id"] for row in response_json]


# ---------------------------------------------------------- list


def test_list_requires_authentication(client: Client) -> None:
    response = client.get(f"{BASE}/")

    assert response.status_code == 403


def test_list_returns_only_the_authenticated_users_items(client: Client) -> None:
    user = make_user()
    other = make_user()
    mine = add(user)
    add(other)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    assert response.status_code == 200
    assert ids(response.json()) == [mine.pk]


def test_list_includes_both_public_and_private_items_for_the_owner(client: Client) -> None:
    user = make_user()
    public_item = add(user, private=False)
    private_item = add(user, private=True)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    assert ids(response.json()) == [public_item.pk, private_item.pk]


def test_list_includes_the_nested_product(client: Client) -> None:
    user = make_user()
    product = make_product()
    add(user, product=product)
    client.force_login(user)

    response = client.get(f"{BASE}/")

    row = response.json()[0]
    assert row["product"]["id"] == product.pk
    assert row["product"]["name"]
    assert "price" in row["product"]


def test_list_is_an_empty_array_when_the_user_has_no_items(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.get(f"{BASE}/")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------- create


def test_create_requires_authentication(client: Client) -> None:
    product = make_product()

    response = client.post(f"{BASE}/", data={"product": product.pk})

    assert response.status_code == 403


def test_create_adds_the_product_to_the_authenticated_users_wishlist(client: Client) -> None:
    user = make_user()
    product = make_product()
    client.force_login(user)

    response = client.post(f"{BASE}/", data={"product": product.pk})

    body = response.json()
    assert response.status_code == 201
    assert ids(body) == [UserWishlistItemModel.objects.get(wishlist__user=user).pk]
    assert body[0]["product"]["id"] == product.pk


def test_create_rejects_a_duplicate_product(client: Client) -> None:
    user = make_user()
    product = make_product()
    add(user, product=product)
    client.force_login(user)

    response = client.post(f"{BASE}/", data={"product": product.pk})

    assert response.status_code == 400
    assert UserWishlistItemModel.objects.filter(wishlist__user=user).count() == 1


def test_create_rejects_an_inactive_product(client: Client) -> None:
    user = make_user()
    product = make_product(active=False)
    client.force_login(user)

    response = client.post(f"{BASE}/", data={"product": product.pk})

    assert response.status_code == 400


def test_create_ignores_any_client_sent_wishlist_or_user_id(client: Client) -> None:
    user = make_user()
    other = make_user()
    product = make_product()
    client.force_login(user)

    response = client.post(
        f"{BASE}/",
        data={
            "product": product.pk,
            "wishlist": wishlist_of(other).pk,
            "user": other.pk,
        },
    )

    assert response.status_code == 201
    item = UserWishlistItemModel.objects.get(product=product)
    assert cast(Any, item).wishlist_id == wishlist_of(user).pk


# ---------------------------------------------------------- remove (destroy)


def test_remove_requires_authentication(client: Client) -> None:
    user = make_user()
    item = add(user)

    response = client.delete(f"{BASE}/{item.pk}/")

    assert response.status_code == 403


def test_remove_deletes_only_the_selected_item(client: Client) -> None:
    user = make_user()
    keep, remove = add(user), add(user)
    client.force_login(user)

    response = client.delete(f"{BASE}/{remove.pk}/")

    assert response.status_code == 200
    remaining = UserWishlistItemModel.objects.filter(wishlist__user=user)
    assert ids(response.json()) == [keep.pk]
    assert list(remaining.values_list("pk", flat=True)) == [keep.pk]


def test_remove_does_not_delete_the_product_from_the_catalog(client: Client) -> None:
    user = make_user()
    product = make_product()
    item = add(user, product=product)
    client.force_login(user)

    client.delete(f"{BASE}/{item.pk}/")

    assert ProductModel.objects.filter(pk=product.pk).exists()


def test_a_user_cannot_remove_another_users_item(client: Client) -> None:
    user = make_user()
    other = make_user()
    other_item = add(other)
    client.force_login(user)

    response = client.delete(f"{BASE}/{other_item.pk}/")

    assert response.status_code == 404
    assert UserWishlistItemModel.objects.filter(pk=other_item.pk).exists()


def test_remove_with_a_nonexistent_item_id_is_not_found(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.delete(f"{BASE}/999999/")

    assert response.status_code == 404


# ---------------------------------------------------------- toggle-privacy


def test_toggle_privacy_requires_authentication(client: Client) -> None:
    user = make_user()
    item = add(user)

    response = client.post(f"{BASE}/{item.pk}/toggle-privacy/")

    assert response.status_code == 403


def test_toggle_privacy_flips_the_flag(client: Client) -> None:
    user = make_user()
    item = add(user, private=False)
    client.force_login(user)

    response = client.post(f"{BASE}/{item.pk}/toggle-privacy/")

    item.refresh_from_db()
    assert response.status_code == 200
    assert cast(bool, item.private) is True
    assert next(row for row in response.json() if row["id"] == item.pk)["private"] is True


def test_toggling_one_items_privacy_does_not_affect_others(client: Client) -> None:
    user = make_user()
    a, b = add(user, private=False), add(user, private=False)
    client.force_login(user)

    client.post(f"{BASE}/{a.pk}/toggle-privacy/")

    b.refresh_from_db()
    assert cast(bool, b.private) is False


def test_a_user_cannot_toggle_privacy_on_another_users_item(client: Client) -> None:
    user = make_user()
    other = make_user()
    other_item = add(other, private=False)
    client.force_login(user)

    response = client.post(f"{BASE}/{other_item.pk}/toggle-privacy/")

    other_item.refresh_from_db()
    assert response.status_code == 404
    assert cast(bool, other_item.private) is False


# ---------------------------------------------------------- move


def test_move_requires_authentication(client: Client) -> None:
    user = make_user()
    item = add(user)

    response = client.post(
        f"{BASE}/{item.pk}/move/",
        data={"direction": "up"},
        content_type="application/json",
    )

    assert response.status_code == 403


def test_move_up_swaps_with_the_previous_item(client: Client) -> None:
    user = make_user()
    a, b = add(user), add(user)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{b.pk}/move/",
        data={"direction": "up"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert ids(response.json()) == [b.pk, a.pk]


def test_move_down_swaps_with_the_next_item(client: Client) -> None:
    user = make_user()
    a, b = add(user), add(user)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{a.pk}/move/",
        data={"direction": "down"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert ids(response.json()) == [b.pk, a.pk]


def test_moving_the_first_item_up_is_a_no_op(client: Client) -> None:
    user = make_user()
    a, b = add(user), add(user)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{a.pk}/move/",
        data={"direction": "up"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert ids(response.json()) == [a.pk, b.pk]


def test_moving_the_last_item_down_is_a_no_op(client: Client) -> None:
    user = make_user()
    a, b = add(user), add(user)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{b.pk}/move/",
        data={"direction": "down"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert ids(response.json()) == [a.pk, b.pk]


def test_move_rejects_an_invalid_direction(client: Client) -> None:
    user = make_user()
    item = add(user)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{item.pk}/move/",
        data={"direction": "sideways"},
        content_type="application/json",
    )

    assert response.status_code == 400


def test_a_user_cannot_move_another_users_item(client: Client) -> None:
    user = make_user()
    other = make_user()
    other_a, other_b = add(other), add(other)
    client.force_login(user)

    response = client.post(
        f"{BASE}/{other_b.pk}/move/",
        data={"direction": "up"},
        content_type="application/json",
    )

    other_a.refresh_from_db()
    other_b.refresh_from_db()
    assert response.status_code == 404
    assert cast(int, other_a.position) == 0
    assert cast(int, other_b.position) == 1


def test_moving_does_not_affect_another_wishlist(client: Client) -> None:
    user = make_user()
    other = make_user()
    _first, b = add(user), add(user)
    other_item = add(other)
    client.force_login(user)

    client.post(
        f"{BASE}/{b.pk}/move/",
        data={"direction": "up"},
        content_type="application/json",
    )

    other_item.refresh_from_db()
    assert cast(int, other_item.position) == 0


# ---------------------------------------------------------- check


def test_check_requires_authentication(client: Client) -> None:
    product = make_product()

    response = client.get(f"{BASE}/check/?product={product.pk}")

    assert response.status_code == 403


def test_check_reports_true_when_the_product_is_in_the_users_wishlist(client: Client) -> None:
    user = make_user()
    product = make_product()
    item = add(user, product=product)
    client.force_login(user)

    response = client.get(f"{BASE}/check/?product={product.pk}")

    body = response.json()
    assert response.status_code == 200
    assert body["in_wishlist"] is True
    assert body["item_id"] == item.pk


def test_check_reports_false_when_the_product_is_absent(client: Client) -> None:
    user = make_user()
    product = make_product()
    client.force_login(user)

    response = client.get(f"{BASE}/check/?product={product.pk}")

    body = response.json()
    assert body["in_wishlist"] is False
    assert body["item_id"] is None


def test_check_is_independent_per_user_for_the_same_product(client: Client) -> None:
    user = make_user()
    other = make_user()
    product = make_product()
    add(other, product=product)
    client.force_login(user)

    response = client.get(f"{BASE}/check/?product={product.pk}")

    assert response.json()["in_wishlist"] is False


def test_check_requires_the_product_query_parameter(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.get(f"{BASE}/check/")

    assert response.status_code == 400


# ---------------------------------------------------------- share-link


def test_share_link_requires_authentication(client: Client) -> None:
    response = client.get(f"{BASE}/share-link/")

    assert response.status_code == 403


def test_share_link_returns_the_callers_own_public_id(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    response = client.get(f"{BASE}/share-link/")

    body = response.json()
    assert response.status_code == 200
    assert body["public_id"] == public_id_of(user)
