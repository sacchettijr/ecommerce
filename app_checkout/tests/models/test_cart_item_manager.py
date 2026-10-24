import threading
from decimal import Decimal
from typing import Any, cast

import pytest

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_checkout.models import CartItemModel
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db


def make_user() -> UserModel:
    return cast(
        UserModel,
        UserFactory(),
    )


def make_product(**kwargs: Any) -> ProductModel:
    return cast(
        ProductModel,
        ProductFactory(**kwargs),
    )


def test_add_item_creates_a_new_row_with_quantity_one() -> None:
    user = make_user()
    product = make_product()

    cart_item = CartItemModel.objects.add_item(
        user=user,
        product=product,
    )

    assert cart_item.pk is not None
    assert cast(int, cart_item.quantity) == 1
    assert (
        CartItemModel.objects.filter(
            user=user,
            product=product,
        ).count()
        == 1
    )


def test_add_item_increments_an_existing_row_instead_of_duplicating() -> None:
    user = make_user()
    product = make_product()

    CartItemModel.objects.add_item(
        user=user,
        product=product,
    )
    cart_item = CartItemModel.objects.add_item(
        user=user,
        product=product,
    )

    assert (
        cast(
            int,
            cart_item.quantity,
        )
        == 2
    )
    assert (
        CartItemModel.objects.filter(
            user=user,
            product=product,
        ).count()
        == 1
    )


def test_add_item_respects_an_explicit_quantity() -> None:
    user = make_user()
    product = make_product()

    cart_item = CartItemModel.objects.add_item(
        user=user,
        product=product,
        quantity=3,
    )

    assert cast(int, cart_item.quantity) == 3


def test_add_item_refreshes_the_stored_price_snapshot_on_increment() -> None:
    user = make_user()
    product = make_product(
        price=Decimal(
            value="10.00",
        ),
    )

    CartItemModel.objects.add_item(
        user=user,
        product=product,
    )
    product.price = Decimal(
        value="20.00",
    )
    product.save(
        update_fields=[
            "price",
        ],
    )
    cart_item = CartItemModel.objects.add_item(
        user=user,
        product=product,
    )

    assert cast(Decimal, cart_item.price) == Decimal(
        value="20.00",
    )


@pytest.mark.django_db(transaction=True)
def test_only_one_row_exists_after_concurrent_adds_for_the_same_user_and_product() -> None:
    user = make_user()
    product = make_product()
    errors: list[BaseException] = []
    lock = threading.Lock()

    def attempt() -> None:
        try:
            CartItemModel.objects.add_item(
                user=user,
                product=product,
            )
        except BaseException as exc:
            with lock:
                errors.append(exc)

    threads = [
        threading.Thread(
            target=attempt,
        )
        for _ in range(10)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    items = CartItemModel.objects.filter(
        user=user,
        product=product,
    )
    assert items.count() == 1
    assert cast(int, items.get().quantity) == 10


def test_summary_for_computes_subtotal_from_live_price_not_the_stored_snapshot() -> None:
    user = make_user()
    product = make_product(
        price=Decimal(
            value="10.00",
        )
    )
    CartItemModel.objects.add_item(
        user=user,
        product=product,
        quantity=2,
    )
    product.price = Decimal(
        value="15.00",
    )
    product.save(
        update_fields=[
            "price",
        ],
    )

    summary = CartItemModel.objects.summary_for(user)

    assert summary.subtotal == Decimal(
        value="30.00",
    )
    assert summary.discount_total == Decimal(
        value="0.00",
    )
    assert summary.total == Decimal(
        value="30.00",
    )


def test_summary_for_sums_multiple_items() -> None:
    user = make_user()
    product_a = make_product(
        price=Decimal(
            value="10.00",
        )
    )
    product_b = make_product(
        price=Decimal(
            value="5.50",
        )
    )
    CartItemModel.objects.add_item(
        user=user,
        product=product_a,
        quantity=2,
    )
    CartItemModel.objects.add_item(
        user=user,
        product=product_b,
        quantity=3,
    )

    summary = CartItemModel.objects.summary_for(user)

    assert summary.subtotal == Decimal(
        value="36.50",
    )
    assert summary.total == Decimal(
        value="36.50",
    )
    assert len(summary.items) == 2


def test_summary_for_only_includes_the_given_users_items() -> None:
    user = make_user()
    other = make_user()
    product = make_product()
    CartItemModel.objects.add_item(
        user=user,
        product=product,
    )
    CartItemModel.objects.add_item(
        user=other,
        product=product,
    )

    summary = CartItemModel.objects.summary_for(user)

    assert len(summary.items) == 1
