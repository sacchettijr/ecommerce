from typing import cast

import pytest
from django.contrib import admin

from app_checkout.admin.CartItemAdmin import CartItemAdmin
from app_checkout.forms import CartItemCreateForm, CartItemUpdateForm
from app_checkout.models import CartItemModel

pytestmark = pytest.mark.django_db


def registered_admin() -> CartItemAdmin:
    return cast(CartItemAdmin, admin.site._registry[CartItemModel])


def test_list_display_configuration_is_unchanged() -> None:
    cart_item_admin = registered_admin()

    assert cart_item_admin.list_display == ("id", "user", "product", "quantity", "price")
    assert cart_item_admin.list_display_links == ("id", "user")
    assert cart_item_admin.list_filter == ("user",)
    assert cart_item_admin.search_fields == ("user__email", "user__name")


def test_add_and_change_use_separate_forms() -> None:
    cart_item_admin = registered_admin()

    assert cart_item_admin.add_form is CartItemCreateForm
    assert cart_item_admin.form is CartItemUpdateForm
