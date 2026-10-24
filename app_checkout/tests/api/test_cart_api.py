from decimal import Decimal
from typing import Any, cast

import pytest
from django.test import Client

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_checkout.models import CartItemModel
from app_checkout.tests.factories import CartItemFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

BASE = "/api/checkout/items"


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def make_product(
    **kwargs: Any,
) -> ProductModel:
    return cast(
        ProductModel,
        ProductFactory(**kwargs),
    )


def add(
    user: UserModel,
    **kwargs: Any,
) -> CartItemModel:
    return cast(
        CartItemModel,
        CartItemFactory(
            user=user,
            **kwargs,
        ),
    )


# ---------------------------------------------------------- authentication / isolation


def test_list_requires_authentication(
    client: Client,
) -> None:
    response = client.get(
        path=f"{BASE}/",
    )

    assert response.status_code == 403


def test_create_requires_authentication(
    client: Client,
) -> None:
    product = make_product()

    response = client.post(
        path=f"{BASE}/",
        data={
            "product": product.pk,
        },
        content_type="application/json",
    )

    assert response.status_code == 403


def test_list_returns_only_the_authenticated_users_items(
    client: Client,
) -> None:
    user = make_user()
    other = make_user()
    mine = add(user)
    add(
        user=other,
    )
    client.force_login(user)

    response = client.get(
        path=f"{BASE}/",
    )

    assert response.status_code == 200
    ids = [row["id"] for row in response.json()["items"]]
    assert ids == [mine.pk]


def test_a_user_cannot_update_another_users_item(
    client: Client,
) -> None:
    user = make_user()
    other = make_user()
    other_item = add(
        user=other,
    )
    client.force_login(user)

    response = client.patch(
        path=f"{BASE}/{other_item.pk}/",
        data={
            "quantity": 5,
        },
        content_type="application/json",
    )

    assert response.status_code == 404
    other_item.refresh_from_db()
    assert (
        cast(
            int,
            other_item.quantity,
        )
        == 1
    )


def test_a_user_cannot_remove_another_users_item(
    client: Client,
) -> None:
    user = make_user()
    other = make_user()
    other_item = add(
        user=other,
    )
    client.force_login(user)

    response = client.delete(
        path=f"{BASE}/{other_item.pk}/",
    )

    assert response.status_code == 404
    assert CartItemModel.objects.filter(
        pk=other_item.pk,
    ).exists()


# ---------------------------------------------------------- add


def test_add_a_new_product_creates_one_item_with_quantity_one(
    client: Client,
) -> None:
    user = make_user()
    product = make_product(
        price=Decimal(
            value="10.00",
        )
    )
    client.force_login(user)

    response = client.post(
        path=f"{BASE}/",
        data={
            "product": product.pk,
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 1
    assert body["subtotal"] == "10.00"
    assert body["discount_total"] == "0.00"
    assert body["total"] == "10.00"


def test_adding_the_same_product_again_increments_instead_of_duplicating(
    client: Client,
) -> None:
    user = make_user()
    product = make_product()
    client.force_login(user)

    client.post(
        path=f"{BASE}/",
        data={"product": product.pk},
        content_type="application/json",
    )
    response = client.post(
        path=f"{BASE}/",
        data={"product": product.pk},
        content_type="application/json",
    )

    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert CartItemModel.objects.filter(user=user, product=product).count() == 1


def test_adding_an_inactive_product_is_rejected(client: Client) -> None:
    user = make_user()
    product = make_product(active=False)
    client.force_login(user)

    response = client.post(
        path=f"{BASE}/",
        data={"product": product.pk},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert (
        CartItemModel.objects.filter(
            user=user,
        ).count()
        == 0
    )


def test_adding_a_nonexistent_product_is_rejected(
    client: Client,
) -> None:
    user = make_user()
    client.force_login(user)

    response = client.post(
        path=f"{BASE}/",
        data={"product": 999999},
        content_type="application/json",
    )

    assert response.status_code == 400


# ---------------------------------------------------------- update quantity


def test_update_quantity_succeeds(client: Client) -> None:
    user = make_user()
    item = add(user, quantity=1)
    client.force_login(user)

    response = client.patch(
        path=f"{BASE}/{item.pk}/",
        data={"quantity": 5},
        content_type="application/json",
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert (
        cast(
            int,
            item.quantity,
        )
        == 5
    )
    assert response.json()["items"][0]["quantity"] == 5


@pytest.mark.parametrize(
    argnames="quantity",
    argvalues=[0, -1, 1.5, "abc", None],
)
def test_update_quantity_rejects_invalid_values(
    client: Client,
    quantity: Any,
) -> None:
    user = make_user()
    item = add(
        user,
        quantity=1,
    )
    client.force_login(user)

    response = client.patch(
        path=f"{BASE}/{item.pk}/",
        data={"quantity": quantity},
        content_type="application/json",
    )

    assert response.status_code == 400
    item.refresh_from_db()
    assert (
        cast(
            int,
            item.quantity,
        )
        == 1
    )


# ---------------------------------------------------------- remove


def test_remove_item_deletes_it_and_returns_the_fresh_summary(
    client: Client,
) -> None:
    user = make_user()
    item = add(user)
    client.force_login(user)

    response = client.delete(
        path=f"{BASE}/{item.pk}/",
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert not CartItemModel.objects.filter(
        pk=item.pk,
    ).exists()


def test_removing_the_only_item_yields_the_empty_state(
    client: Client,
) -> None:
    user = make_user()
    item = add(user)
    client.force_login(user)

    response = client.delete(
        path=f"{BASE}/{item.pk}/",
    )

    body = response.json()
    assert body["items"] == []
    assert body["subtotal"] == "0.00"
    assert body["total"] == "0.00"


# ---------------------------------------------------------- deactivation cascade


def test_deactivating_a_product_removes_it_from_every_cart(
    client: Client,
) -> None:
    user = make_user()
    other = make_user()
    product = make_product()
    add(
        user,
        product=product,
    )
    add(
        user=other,
        product=product,
    )

    product.active = False
    product.save(
        update_fields=[
            "active",
        ],
    )

    assert (
        CartItemModel.objects.filter(
            product=product,
        ).count()
        == 0
    )


def test_a_deactivated_product_cannot_be_re_added(
    client: Client,
) -> None:
    user = make_user()
    product = make_product()
    add(user, product=product)
    product.active = False
    product.save(
        update_fields=[
            "active",
        ],
    )
    client.force_login(user)

    response = client.post(
        path=f"{BASE}/",
        data={"product": product.pk},
        content_type="application/json",
    )

    assert response.status_code == 400


# ---------------------------------------------------------- persistence across sessions


def test_cart_persists_across_separate_authenticated_sessions(
    client: Client,
) -> None:
    user = make_user()
    add(user)

    second_session = Client()
    second_session.force_login(user)
    response = second_session.get(
        path=f"{BASE}/",
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_logout_does_not_delete_cart_items(client: Client) -> None:
    user = make_user()
    item = add(user)
    client.force_login(user)
    client.post(
        path="/api/account/logout/",
    )

    second_login = Client()
    second_login.force_login(user)
    response = second_login.get(
        path=f"{BASE}/",
    )

    assert response.status_code == 200
    ids = [row["id"] for row in response.json()["items"]]
    assert ids == [item.pk]


# ---------------------------------------------------------- totals math


def test_subtotal_and_total_use_decimal_and_sum_all_items(
    client: Client,
) -> None:
    user = make_user()
    product_a = make_product(
        price=Decimal(
            value="3.33",
        )
    )
    product_b = make_product(
        price=Decimal(
            value="6.67",
        )
    )
    add(
        user,
        product=product_a,
        quantity=3,
    )
    add(
        user,
        product=product_b,
        quantity=1,
    )
    client.force_login(user)

    response = client.get(
        path=f"{BASE}/",
    )

    body = response.json()
    assert body["subtotal"] == "16.66"
    assert body["discount_total"] == "0.00"
    assert body["total"] == "16.66"
