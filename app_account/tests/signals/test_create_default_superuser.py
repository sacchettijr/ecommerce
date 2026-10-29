from typing import cast

import pytest
from django.apps import AppConfig, apps

from app_account.models import UserModel
from app_account.signals.create_default_superuser import create_default_superuser
from app_account.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

ENV_VARS = (
    "DJANGO_SUPERUSER_EMAIL",
    "DJANGO_SUPERUSER_PASSWORD",
    "DJANGO_SUPERUSER_NAME",
    "DJANGO_SUPERUSER_DATE_BIRTH",
)


@pytest.fixture(autouse=True)
def _clean_slate(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    #   The real post_migrate run that builds the test database already fires this
    #   same signal (with whatever DJANGO_SUPERUSER_* vars the dev environment has),
    #   so a superuser may already exist by the time this test starts — clear it to
    #   get the clean "fresh install" precondition each test actually exercises.
    UserModel.objects.filter(is_superuser=True).delete()


def account_app_config() -> AppConfig:
    return apps.get_app_config("account")


def test_creates_the_documented_weak_fallback_superuser_when_no_env_vars_are_set() -> None:
    #   This is the known, already-flagged weak-credential fallback
    #   (see .claude/memory/known_issues.md) — this test documents its exact,
    #   current behavior as a regression guard, it does not endorse it.
    assert not UserModel.objects.filter(is_superuser=True).exists()

    create_default_superuser(sender=account_app_config())

    admin = UserModel.objects.get(email="admin@example.com")
    assert admin.is_superuser is True
    assert cast(bool, admin.is_staff) is True
    assert admin.check_password("admin123") is True
    assert cast(str, admin.name) == "Administrador"


def test_uses_the_djangosuperuser_env_vars_when_they_are_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "owner@example.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "a-strong-password")
    monkeypatch.setenv("DJANGO_SUPERUSER_NAME", "Real Owner")
    monkeypatch.setenv("DJANGO_SUPERUSER_DATE_BIRTH", "1990-05-15")

    create_default_superuser(sender=account_app_config())

    admin = UserModel.objects.get(email="owner@example.com")
    assert admin.check_password("a-strong-password") is True
    assert cast(str, admin.name) == "Real Owner"
    assert UserModel.objects.filter(email="admin@example.com").exists() is False


def test_does_nothing_when_a_superuser_already_exists() -> None:
    UserFactory(is_superuser=True, is_staff=True)
    existing_count = UserModel.objects.count()

    create_default_superuser(sender=account_app_config())

    assert UserModel.objects.count() == existing_count
    assert UserModel.objects.filter(email="admin@example.com").exists() is False


def test_is_idempotent_across_repeated_post_migrate_runs() -> None:
    create_default_superuser(sender=account_app_config())
    create_default_superuser(sender=account_app_config())

    assert UserModel.objects.filter(is_superuser=True).count() == 1
