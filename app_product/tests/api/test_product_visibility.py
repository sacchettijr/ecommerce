from typing import Any, cast

import pytest
from django.test import Client

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductCategoryFactory, ProductFactory

pytestmark = pytest.mark.django_db


def make_staff_client() -> Client:
    client = Client()
    user = cast(UserModel, UserFactory(is_staff=True, is_superuser=True))
    client.force_login(user)
    return client


# ---------------------------------------------------- list: anonymous browsing


def test_anonymous_users_can_list_products() -> None:
    ProductFactory()

    response = Client().get("/api/product/products/")

    assert response.status_code == 200


def test_inactive_products_are_excluded_from_the_public_list_for_anonymous_users() -> None:
    active = cast(ProductModel, ProductFactory(active=True))
    inactive = cast(ProductModel, ProductFactory(active=False))

    response = Client().get("/api/product/products/")

    ids = {row["id"] for row in response.json()["results"]}
    assert active.pk in ids
    assert inactive.pk not in ids


def test_inactive_products_are_excluded_from_the_public_list_even_for_staff() -> None:
    #   Unlike the wishlist's staff exception, the public product list/detail
    #   endpoints have no staff carve-out at all — they exist purely as the public
    #   catalog, so an inactive product never appears here for anyone.
    inactive = cast(ProductModel, ProductFactory(active=False))

    response = make_staff_client().get("/api/product/products/")

    ids = {row["id"] for row in response.json()["results"]}
    assert inactive.pk not in ids


def test_list_can_be_filtered_by_category_slug() -> None:
    category = cast(Any, ProductCategoryFactory())
    other_category = cast(Any, ProductCategoryFactory())
    matching = cast(ProductModel, ProductFactory(category=category))
    ProductFactory(category=other_category)

    response = Client().get(f"/api/product/products/?category={category.slug}")

    ids = {row["id"] for row in response.json()["results"]}
    assert ids == {matching.pk}


# -------------------------------------------------- detail: anonymous browsing


def test_anonymous_users_can_retrieve_an_active_products_detail_by_slug() -> None:
    product = cast(Any, ProductFactory(active=True))

    response = Client().get(f"/api/product/products/{product.slug}/")

    assert response.status_code == 200
    assert response.json()["id"] == product.pk


def test_an_inactive_products_detail_404s_for_anonymous_users() -> None:
    product = cast(Any, ProductFactory(active=False))

    response = Client().get(f"/api/product/products/{product.slug}/")

    assert response.status_code == 404


def test_an_inactive_products_detail_404s_even_for_staff() -> None:
    product = cast(Any, ProductFactory(active=False))

    response = make_staff_client().get(f"/api/product/products/{product.slug}/")

    assert response.status_code == 404


# ------------------------------------------------------------------ categories


def test_anonymous_users_can_list_active_categories() -> None:
    active = cast(Any, ProductCategoryFactory(active=True))
    inactive = cast(Any, ProductCategoryFactory(active=False))

    response = Client().get("/api/product/categories/")

    ids = {row["id"] for row in response.json()["results"]}
    assert active.pk in ids
    assert inactive.pk not in ids
