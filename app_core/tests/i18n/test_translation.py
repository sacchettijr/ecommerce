import pytest
from django.test import Client
from django.utils import translation
from django.utils.translation import gettext

from app_account.tests.factories import UserFactory
from utils.env import env
from utils.validator import validate_name

pytestmark = pytest.mark.django_db

PASSWORD = env(name="USER_TEST_PASSWORD")


# --------------------------------------------------- settings-level regression guard
#
#   LANGUAGES only declared pt-br/en/es until 2026-10-18; fr/it requests silently fell
#   back to English regardless of catalog content. This guards against that regression
#   recurring (see .claude/memory/known_issues.md / context/domain.md).


def test_all_five_required_languages_are_declared() -> None:
    from django.conf import settings

    codes = {code for code, _label in settings.LANGUAGES}
    assert codes == {"pt-br", "en", "es", "fr", "it"}


# --------------------------------------------------------- translation.override, direct


def test_gettext_returns_the_source_string_for_english() -> None:
    with translation.override("en"):
        assert gettext("This account has been deactivated.") == "This account has been deactivated."


def test_gettext_returns_the_portuguese_translation() -> None:
    with translation.override("pt-br"):
        assert gettext("This account has been deactivated.") == "Esta conta foi desativada."


def test_gettext_returns_the_french_translation() -> None:
    with translation.override("fr"):
        assert gettext("This account has been deactivated.") == "Ce compte a été désactivé."


def test_gettext_returns_the_italian_translation() -> None:
    expected = "Questo account è stato disattivato."
    with translation.override("it"):
        assert gettext("This account has been deactivated.") == expected


def test_a_validator_error_message_is_translated_too() -> None:
    #   utils/validator.py's gettext_lazy messages must resolve the same way as any
    #   other translated string, since the validator itself runs locale-agnostic code.
    with translation.override("pt-br"):
        try:
            validate_name(value="")
        except Exception as exc:
            assert "O nome não pode ficar vazio." in str(exc)
        else:
            pytest.fail("validate_name('') was expected to raise")


# -------------------------------------------- full-stack: Accept-Language -> LocaleMiddleware


def test_accept_language_header_selects_the_response_language_end_to_end() -> None:
    user = UserFactory(is_active=False)

    response_en = Client().post(
        "/api/account/login/",
        data={"email": user.email, "password": PASSWORD},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="en",
    )
    response_pt = Client().post(
        "/api/account/login/",
        data={"email": user.email, "password": PASSWORD},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="pt-br",
    )

    assert response_en.json()["non_field_errors"] == ["This account has been deactivated."]
    assert response_pt.json()["non_field_errors"] == ["Esta conta foi desativada."]
    #   Same underlying error code regardless of language — only the message text changes.
    assert response_en.json()["code"] == response_pt.json()["code"] == "inactive"


def test_accept_language_fr_no_longer_falls_back_to_english() -> None:
    #   Regression guard for the fixed 2026-10-18 bug: fr/it used to silently render in
    #   English because LANGUAGES only declared pt-br/en/es at the time.
    user = UserFactory(is_active=False)

    response = Client().post(
        "/api/account/login/",
        data={"email": user.email, "password": PASSWORD},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="fr",
    )

    assert response.json()["non_field_errors"] == ["Ce compte a été désactivé."]


def test_an_unsupported_language_falls_back_to_the_default() -> None:
    user = UserFactory(is_active=False)

    response = Client().post(
        "/api/account/login/",
        data={"email": user.email, "password": PASSWORD},
        content_type="application/json",
        HTTP_ACCEPT_LANGUAGE="de",
    )

    assert response.json()["non_field_errors"] == ["This account has been deactivated."]
