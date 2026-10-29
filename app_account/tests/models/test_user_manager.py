from typing import cast

import pytest

from app_account.models import UserModel

pytestmark = pytest.mark.django_db


# ----------------------------------------------------------- create_user


def test_create_user_requires_an_email() -> None:
    with pytest.raises(ValueError, match=r"Email is required\."):
        UserModel.objects.create_user(
            email="",
            password="a-strong-password",
            name="No Email",
            date_birth="2000-01-01",
        )


def test_create_user_normalizes_the_email_case() -> None:
    user = UserModel.objects.create_user(
        email="someone@EXAMPLE.com",
        password="a-strong-password",
        name="Someone",
        date_birth="2000-01-01",
    )

    assert cast(str, user.email) == "someone@example.com"


def test_create_user_hashes_the_password() -> None:
    user = UserModel.objects.create_user(
        email="hashed@example.com",
        password="a-strong-password",
        name="Someone",
        date_birth="2000-01-01",
    )

    assert user.password != "a-strong-password"
    assert user.check_password("a-strong-password") is True


def test_create_user_defaults_to_non_staff_non_superuser() -> None:
    user = UserModel.objects.create_user(
        email="plain@example.com",
        password="a-strong-password",
        name="Someone",
        date_birth="2000-01-01",
    )

    assert cast(bool, user.is_staff) is False
    assert user.is_superuser is False


# -------------------------------------------------------- create_superuser


def test_create_superuser_rejects_an_explicit_is_staff_false() -> None:
    with pytest.raises(ValueError, match="is_staff=True"):
        UserModel.objects.create_superuser(
            email="notstaff@example.com",
            password="a-strong-password",
            name="Not Staff",
            date_birth="2000-01-01",
            is_staff=False,
        )


def test_create_superuser_rejects_an_explicit_is_superuser_false() -> None:
    with pytest.raises(ValueError, match="is_superuser=True"):
        UserModel.objects.create_superuser(
            email="notsuperuser@example.com",
            password="a-strong-password",
            name="Not Superuser",
            date_birth="2000-01-01",
            is_superuser=False,
        )


def test_create_superuser_sets_every_permission_flag_by_default() -> None:
    user = UserModel.objects.create_superuser(
        email="root@example.com",
        password="a-strong-password",
        name="Root",
        date_birth="2000-01-01",
    )

    assert cast(bool, user.is_staff) is True
    assert user.is_superuser is True
    assert user.is_active is True
    assert cast(bool, user.is_email_verified) is True
