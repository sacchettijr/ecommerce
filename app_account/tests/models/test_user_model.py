from typing import cast

import pytest
from django.core import mail

from app_account.models import UserModel
from app_account.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def make_user(**kwargs: object) -> UserModel:
    return cast(UserModel, UserFactory(**kwargs))


def test_str_combines_name_and_email() -> None:
    user = make_user(name="Jane Doe", email="jane@example.com")

    assert str(user) == "Jane Doe <jane@example.com>"


def test_get_full_name_returns_the_whole_name() -> None:
    user = make_user(name="Jane Middle Doe")

    assert user.get_full_name() == "Jane Middle Doe"


def test_get_short_name_returns_only_the_first_word() -> None:
    user = make_user(name="Jane Middle Doe")

    assert user.get_short_name() == "Jane"


def test_save_collapses_internal_whitespace_in_the_name() -> None:
    user = make_user(name="Jane   Middle    Doe")

    user.refresh_from_db()
    assert cast(str, user.name) == "Jane Middle Doe"


def test_save_lowercases_the_whole_email() -> None:
    user = make_user(email="Mixed.Case@EXAMPLE.com")

    user.refresh_from_db()
    assert cast(str, user.email) == "mixed.case@example.com"


def test_user_email_confirmation_sends_to_the_users_own_email() -> None:
    user = make_user(email="recipient@example.com")

    user.user_email_confirmation(
        subject="Confirm your account",
        message="Click the link below.",
    )

    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.to == ["recipient@example.com"]
    assert sent.subject == "Confirm your account"
    assert sent.body == "Click the link below."
