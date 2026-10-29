from typing import Any, cast

import pytest

from app_checkout.models import CartItemModel
from app_checkout.tests.factories import CartItemFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db


def test_deactivating_a_product_deletes_its_cart_items() -> None:
    item = cast(Any, CartItemFactory())
    product = cast(ProductModel, item.product)

    product.active = False
    product.save()

    assert not CartItemModel.objects.filter(pk=item.pk).exists()


def test_saving_a_product_as_still_active_does_not_touch_cart_items() -> None:
    item = cast(Any, CartItemFactory())
    product = cast(ProductModel, item.product)

    product.active = True
    product.save()

    assert CartItemModel.objects.filter(pk=item.pk).exists()


def test_re_saving_an_already_inactive_product_does_not_error_with_no_cart_items() -> None:
    product = cast(ProductModel, ProductFactory(active=False))

    product.active = False
    product.save()  # must not raise even though there is nothing to delete


def test_deactivating_a_product_only_removes_that_products_own_cart_items() -> None:
    target_item = cast(Any, CartItemFactory())
    other_item = cast(Any, CartItemFactory())

    target_product = cast(ProductModel, target_item.product)
    target_product.active = False
    target_product.save()

    assert not CartItemModel.objects.filter(pk=target_item.pk).exists()
    assert CartItemModel.objects.filter(pk=other_item.pk).exists()


def test_deactivating_a_product_removes_it_from_every_users_cart() -> None:
    product = cast(ProductModel, ProductFactory(active=True))
    first = cast(Any, CartItemFactory(product=product))
    second = cast(Any, CartItemFactory(product=product))

    product.active = False
    product.save()

    assert not CartItemModel.objects.filter(pk__in=[first.pk, second.pk]).exists()
