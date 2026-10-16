from typing import cast

import pytest
from django.contrib import admin
from django.http import HttpRequest
from django.test import RequestFactory

from app_account.models import UserAddressModel, UserModel
from app_account.tests.factories import UserAddressFactory, UserFactory

pytestmark = pytest.mark.django_db

EXPECTED_STANDALONE_ADD_ORDER = [
    "primary",
    "user",
    "street",
    "number",
    "complement",
    "reference",
    "district",
    "postal_code",
    "country",
    "state",
    "city",
]
EXPECTED_INLINE_FIELDS = [
    "primary",
    "street",
    "number",
    "complement",
    "reference",
    "district",
    "postal_code",
    "country",
    "state",
    "city",
]


def staff_request(path: str = "/admin/app_account/useraddressmodel/") -> HttpRequest:
    request = RequestFactory().get(path)
    request.user = cast(UserModel, UserFactory(is_staff=True, is_superuser=True))
    return request


def test_standalone_admin_add_form_field_order() -> None:
    address_admin = admin.site._registry[UserAddressModel]
    request = staff_request()

    add_form = address_admin.get_form(request, obj=None)

    assert list(add_form.base_fields.keys()) == EXPECTED_STANDALONE_ADD_ORDER


def test_standalone_admin_change_form_field_order() -> None:
    address_admin = admin.site._registry[UserAddressModel]
    request = staff_request()
    address = cast(UserAddressModel, UserAddressFactory())

    change_form = address_admin.get_form(request, obj=address)

    assert list(change_form.base_fields.keys()) == EXPECTED_STANDALONE_ADD_ORDER


def test_inline_field_order_is_country_state_city() -> None:
    user_admin = admin.site._registry[UserModel]
    request = staff_request(path="/admin/app_account/usermodel/")

    inline_instances = user_admin.get_inline_instances(request)
    address_inline = next(
        inline for inline in inline_instances if type(inline).__name__ == "UserAddressInlineAdmin"
    )

    assert list(address_inline.get_fields(request)) == EXPECTED_INLINE_FIELDS
