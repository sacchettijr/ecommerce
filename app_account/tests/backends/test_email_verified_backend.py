from typing import cast

import pytest

from app_account.backends.EmailVerifiedModelBackend import EmailVerifiedModelBackend
from app_account.models import UserModel
from app_account.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def make_backend() -> EmailVerifiedModelBackend:
    return EmailVerifiedModelBackend()


def test_rejects_an_object_that_is_not_a_user_model() -> None:
    backend = make_backend()

    assert backend.user_can_authenticate(object()) is False


def test_rejects_none() -> None:
    backend = make_backend()

    assert backend.user_can_authenticate(None) is False


def test_accepts_an_active_and_email_verified_user() -> None:
    backend = make_backend()
    user = cast(UserModel, UserFactory(is_active=True, is_email_verified=True))

    assert backend.user_can_authenticate(user) is True


def test_rejects_an_inactive_user() -> None:
    backend = make_backend()
    user = cast(UserModel, UserFactory(is_active=False, is_email_verified=True))

    assert backend.user_can_authenticate(user) is False


def test_rejects_a_user_with_an_unverified_email() -> None:
    backend = make_backend()
    user = cast(UserModel, UserFactory(is_active=True, is_email_verified=False))

    assert backend.user_can_authenticate(user) is False
