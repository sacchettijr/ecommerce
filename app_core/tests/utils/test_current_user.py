from typing import cast

import pytest

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from utils.current_user import get_current_user, set_current_user

pytestmark = pytest.mark.django_db


def test_get_current_user_defaults_to_none() -> None:
    assert get_current_user() is None


def test_set_current_user_makes_it_visible_to_get_current_user() -> None:
    user = cast(UserModel, UserFactory())

    try:
        set_current_user(user=user)
        assert get_current_user() is user
    finally:
        set_current_user(user=None)


def test_set_current_user_none_clears_it() -> None:
    user = cast(UserModel, UserFactory())

    set_current_user(user=user)
    set_current_user(user=None)

    assert get_current_user() is None
