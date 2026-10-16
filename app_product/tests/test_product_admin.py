from typing import cast

import pytest
from django.contrib import admin
from django.http import HttpRequest
from django.test import RequestFactory

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

EXPECTED_ADD_ORDER = [
    "active",
    "category",
    "name",
    "price",
    "thumbnail",
    "description",
]
EXPECTED_CHANGE_ORDER = [
    "active",
    "category",
    "name",
    "slug",
    "price",
    "thumbnail",
    "description",
]


def staff_request() -> HttpRequest:
    request = RequestFactory().get("/admin/app_product/productmodel/")
    request.user = cast(UserModel, UserFactory(is_staff=True, is_superuser=True))
    return request


def test_add_form_field_order() -> None:
    product_admin = admin.site._registry[ProductModel]
    request = staff_request()

    add_form = product_admin.get_form(request, obj=None)

    assert list(add_form.base_fields.keys()) == EXPECTED_ADD_ORDER


def test_change_form_field_order() -> None:
    product_admin = admin.site._registry[ProductModel]
    request = staff_request()
    product = cast(ProductModel, ProductFactory())

    fieldsets = product_admin.get_fieldsets(request, obj=product)

    assert len(fieldsets) == 1
    _name, options = fieldsets[0]
    assert list(options["fields"]) == EXPECTED_CHANGE_ORDER


def test_product_images_inline_still_renders_below_the_main_fields() -> None:
    product_admin = admin.site._registry[ProductModel]

    assert [inline.__name__ for inline in product_admin.inlines] == [
        "ProductImageInlineAdmin",
    ]


def test_list_page_configuration_is_unchanged() -> None:
    product_admin = admin.site._registry[ProductModel]

    assert product_admin.list_display == (
        "id",
        "active",
        "name",
        "slug",
        "category",
        "created_at",
    )
    assert product_admin.list_filter == ("active", "created_at", "updated_at")
    assert product_admin.search_fields == ("name", "slug", "category__name")
