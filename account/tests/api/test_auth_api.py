import re
from collections.abc import Iterator
from typing import Any, cast
from unittest.mock import patch

import pytest
from celery import current_app
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.test import Client
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.models import UserModel
from account.tasks import (
    send_email_verification_email,
    send_password_reset_email,
)
from account.tests.factories import UserFactory
from account.tokens import email_verification_token
from utils.env import env
from utils.redirect import safe_next_path

pytestmark = pytest.mark.django_db

PASSWORD = env(name="USER_TEST_PASSWORD")
NEW_PASSWORD = "An0ther-Str0ng#Pass"
BASE = "/api/account"


@pytest.fixture(autouse=True)
def clean_throttle_cache() -> Iterator[None]:
    #   Os contadores de throttle ficam no cache (Redis): zera para os testes serem independentes.
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def run_celery_tasks_inline() -> Iterator[None]:
    #   Nada de broker nos testes: as tarefas rodam na hora e os e-mails caem em mail.outbox.
    def verification_send_task(*, name: str, kwargs: dict[str, Any]) -> None:
        send_email_verification_email.apply(kwargs=kwargs).get()

    def reset_delay(**kwargs: Any) -> None:
        send_password_reset_email.apply(kwargs=kwargs).get()

    with (
        patch(
            "celery.app.base.Celery.send_task",
            side_effect=verification_send_task,
        ),
        patch(
            "account.forms.PasswordResetForm.send_password_reset_email.delay",
            side_effect=reset_delay,
        ),
    ):
        yield


def make_user(**kwargs: Any) -> UserModel:
    return cast(UserModel, UserFactory(**kwargs))


def post(client: Client, path: str, data: dict[str, Any]) -> Any:
    return client.post(
        f"{BASE}/{path}/",
        data=data,
        content_type="application/json",
    )


def signup_data(**overrides: Any) -> dict[str, Any]:
    return {
        "name": "Maria da Silva",
        "email": "maria@example.com",
        "date_birth": "1990-05-20",
        "phone": "",
        "password1": NEW_PASSWORD,
        "password2": NEW_PASSWORD,
        **overrides,
    }


def email_of(user: UserModel) -> str:
    return cast(str, user.email)


def is_verified(user: UserModel) -> bool:
    return cast(bool, user.is_email_verified)


def sent_message() -> tuple[EmailMultiAlternatives, str]:
    message = cast(EmailMultiAlternatives, mail.outbox[0])
    return message, str(message.alternatives[0][0])


def uid_of(user: UserModel) -> str:
    return urlsafe_base64_encode(force_bytes(user.pk))


def test_verification_task_is_registered_under_the_name_used_to_enqueue_it() -> None:
    #   O envio usa send_task(name=...): se os nomes divergirem, o worker descarta a tarefa
    #   ("unregistered task") e o e-mail nunca sai, mesmo com todos os outros testes passando.
    assert send_email_verification_email.name == "account.tasks.send_email_verification_email"
    assert "account.tasks.send_email_verification_email" in current_app.tasks


# ---------------------------------------------------------- safe_next_path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("/checkout", "/checkout"),
        ("/product/mouse?x=1&y=2", "/product/mouse?x=1&y=2"),
        ("", ""),
        (None, ""),
        ("checkout", ""),
        ("//evil.com", ""),
        ("/\\evil.com", ""),
        ("https://evil.com", ""),
        ("javascript:alert(1)", ""),
        ("/%09/evil.com", "/%09/evil.com"),
    ],
)
def test_safe_next_path(value: str | None, expected: str) -> None:
    assert safe_next_path(value) == expected


# ---------------------------------------------------------- session / csrf


def test_session_returns_null_user_and_the_csrf_cookie(client: Client) -> None:
    response = client.get(f"{BASE}/session/")

    assert response.status_code == 200
    assert response.json() == {"user": None}
    assert "csrftoken" in response.cookies


def test_session_returns_the_logged_in_user(client: Client) -> None:
    user = make_user()
    client.force_login(user)

    payload = client.get(f"{BASE}/session/").json()

    assert payload["user"] == {
        "id": user.pk,
        "name": cast(str, user.name),
        "email": email_of(user),
        "is_staff": False,
    }
    assert "password" not in payload["user"]


@pytest.mark.parametrize("is_staff", [True, False])
def test_session_and_login_report_is_staff_so_the_frontend_can_show_the_admin_link(
    client: Client,
    is_staff: bool,
) -> None:
    #   O front só decide se mostra "Acesso ao admin" com isto; a permissão real continua
    #   sendo o Django Admin conferindo is_staff a cada requisição, não o valor deste payload.
    user = make_user(is_staff=is_staff)

    login_payload = post(client, "login", {"email": email_of(user), "password": PASSWORD}).json()
    session_payload = client.get(f"{BASE}/session/").json()

    assert login_payload["user"]["is_staff"] is is_staff
    assert session_payload["user"]["is_staff"] is is_staff


def test_post_without_csrf_token_is_rejected() -> None:
    strict = Client(enforce_csrf_checks=True)

    response = post(strict, "login", {"email": "a@example.com", "password": "x"})

    assert response.status_code == 403


def test_post_with_csrf_token_is_accepted() -> None:
    strict = Client(enforce_csrf_checks=True)
    token = strict.get(f"{BASE}/session/").cookies["csrftoken"].value

    response = strict.post(
        f"{BASE}/login/",
        data={"email": "a@example.com", "password": "x"},
        content_type="application/json",
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400


# ---------------------------------------------------------- login / logout


def test_login_success_starts_a_session(client: Client) -> None:
    user = make_user()

    response = post(client, "login", {"email": email_of(user), "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["user"]["email"] == email_of(user)
    assert client.get(f"{BASE}/session/").json()["user"]["id"] == user.pk


def test_login_invalid_credentials_is_a_form_level_error(client: Client) -> None:
    user = make_user()

    response = post(client, "login", {"email": email_of(user), "password": "wrong-password"})

    body = response.json()
    assert response.status_code == 400
    assert body["non_field_errors"]
    assert "email" not in body
    assert client.get(f"{BASE}/session/").json()["user"] is None


def test_login_missing_fields_are_field_level_errors(client: Client) -> None:
    body = post(client, "login", {}).json()

    assert body["email"]
    assert body["password"]


def test_login_with_unconfirmed_email_reports_a_code_and_does_not_log_in(client: Client) -> None:
    user = make_user(is_email_verified=False)

    response = post(client, "login", {"email": email_of(user), "password": PASSWORD})

    assert response.status_code == 400
    assert response.json()["code"] == "email_not_verified"
    assert client.get(f"{BASE}/session/").json()["user"] is None


def test_login_of_an_inactive_account_is_rejected(client: Client) -> None:
    user = make_user(is_active=False)

    response = post(client, "login", {"email": email_of(user), "password": PASSWORD})

    assert response.status_code == 400
    assert client.get(f"{BASE}/session/").json()["user"] is None


def test_login_is_throttled(client: Client) -> None:
    statuses = [
        post(client, "login", {"email": "x@example.com", "password": "wrong"}).status_code
        for _ in range(11)
    ]

    assert statuses[:10] == [400] * 10
    assert statuses[10] == 429


def test_logout_ends_the_session(client: Client) -> None:
    client.force_login(make_user())

    response = post(client, "logout", {})

    assert response.status_code == 204
    assert client.get(f"{BASE}/session/").json()["user"] is None


# ---------------------------------------------------------- signup + verification email


def test_signup_creates_an_unverified_user_and_sends_the_confirmation_email(client: Client) -> None:
    response = post(client, "signup", signup_data(next="/checkout"))

    user = UserModel.objects.get(email="maria@example.com")
    assert response.status_code == 201
    assert is_verified(user) is False
    assert user.check_password(NEW_PASSWORD)

    assert len(mail.outbox) == 1
    message, html = sent_message()
    assert message.to == ["maria@example.com"]
    assert "E-Commerce" in message.subject
    assert "<!DOCTYPE html>" in html
    assert "Confirmar e-mail" in html

    #   O link do e-mail (texto e HTML) abre a página React e leva um token válido + o next.
    for content in (message.body, html):
        match = re.search(
            r"/email-verification/(?P<uid>[^/\s]+)/(?P<token>[^/\s]+)/\?next=%2Fcheckout",
            str(content),
        )
        assert match is not None
        assert match["uid"] == uid_of(user)
        assert email_verification_token.check_token(user, match["token"])


def test_signup_drops_an_unsafe_next(client: Client) -> None:
    post(client, "signup", signup_data(next="https://evil.com/steal"))

    assert "next=" not in mail.outbox[0].body
    assert "evil.com" not in mail.outbox[0].body


def test_signup_confirmation_email_link_uses_frontend_url(
    client: Client,
    settings: Any,
) -> None:
    settings.FRONTEND_URL = "https://shop.example.com"

    post(client, "signup", signup_data())

    message, html = sent_message()
    user = UserModel.objects.get(email="maria@example.com")
    assert f"https://shop.example.com/email-verification/{uid_of(user)}/" in message.body
    assert f"https://shop.example.com/email-verification/{uid_of(user)}/" in html


def test_signup_field_errors_come_from_the_django_form(client: Client) -> None:
    make_user(email="taken@example.com")

    body = post(
        client,
        "signup",
        signup_data(
            email="taken@example.com",
            name="A",
            password1="12345678",
            password2="different",
        ),
    ).json()

    assert body["email"]
    assert body["password2"]
    assert not mail.outbox
    assert UserModel.objects.filter(email="taken@example.com").count() == 1


def test_signup_requires_the_mandatory_fields(client: Client) -> None:
    response = post(client, "signup", {})
    body = response.json()

    assert response.status_code == 400
    for field in ("name", "email", "date_birth", "password1", "password2"):
        assert body[field]


def test_signup_email_normalization_prevents_a_duplicate_with_other_casing(client: Client) -> None:
    make_user(email="dup@example.com")

    body = post(client, "signup", signup_data(email="DUP@Example.com")).json()

    assert body["email"]


# ---------------------------------------------------------- email verification


def confirm(client: Client, uid: str, token: str) -> Any:
    return post(client, "email-verification/confirm", {"uid": uid, "token": token})


def test_email_confirmation_activates_the_account(client: Client) -> None:
    user = make_user(is_email_verified=False)

    response = confirm(client, uid_of(user), email_verification_token.make_token(user))

    user.refresh_from_db()
    assert response.status_code == 200
    assert is_verified(user) is True
    assert post(client, "login", {"email": email_of(user), "password": PASSWORD}).status_code == 200


def test_email_confirmation_link_cannot_be_reused(client: Client) -> None:
    user = make_user(is_email_verified=False)
    token = email_verification_token.make_token(user)

    assert confirm(client, uid_of(user), token).status_code == 200
    second = confirm(client, uid_of(user), token)

    assert second.status_code == 400
    assert second.json()["code"] == "invalid_link"


def broken_link(kind: str, user: UserModel) -> tuple[str, str]:
    valid_token = email_verification_token.make_token(user)

    match kind:
        case "bad-token":
            return uid_of(user), "not-a-real-token"
        case "bad-uid":
            return "!!!", valid_token
        case "reversed-uid":
            return uid_of(user)[::-1], valid_token
        case "unknown-user":
            return urlsafe_base64_encode(b"999999"), valid_token
        case _:
            return uid_of(user), default_token_generator.make_token(user)


@pytest.mark.parametrize(
    "kind",
    ["bad-token", "bad-uid", "reversed-uid", "unknown-user", "password-reset-token"],
)
def test_invalid_confirmation_links_are_rejected(client: Client, kind: str) -> None:
    user = make_user(is_email_verified=False)

    response = confirm(client, *broken_link(kind, user))

    user.refresh_from_db()
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_link"
    assert is_verified(user) is False


def test_expired_confirmation_link_is_rejected(client: Client, settings: Any) -> None:
    user = make_user(is_email_verified=False)
    token = email_verification_token.make_token(user)
    settings.PASSWORD_RESET_TIMEOUT = -1

    response = confirm(client, uid_of(user), token)

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_link"


def test_confirmation_requires_uid_and_token(client: Client) -> None:
    response = post(client, "email-verification/confirm", {})

    assert response.status_code == 400
    assert response.json()["uid"]


def test_resend_sends_a_new_email_for_an_unverified_account(client: Client) -> None:
    user = make_user(is_email_verified=False)

    response = post(client, "email-verification/resend", {"email": email_of(user), "next": "/cart"})

    assert response.status_code == 202
    assert len(mail.outbox) == 1
    assert "next=%2Fcart" in mail.outbox[0].body


@pytest.mark.parametrize("known", ["missing", "verified"])
def test_resend_answers_the_same_and_sends_nothing_otherwise(client: Client, known: str) -> None:
    email = "nobody@example.com" if known == "missing" else email_of(make_user())

    response = post(client, "email-verification/resend", {"email": email})

    assert response.status_code == 202
    assert response.json() == {}
    assert not mail.outbox


def test_resend_validates_the_email_format(client: Client) -> None:
    response = post(client, "email-verification/resend", {"email": "not-an-email"})

    assert response.status_code == 400
    assert response.json()["email"]


# ---------------------------------------------------------- password reset


def test_password_reset_request_sends_the_email_pointing_to_the_react_page(client: Client) -> None:
    user = make_user()

    response = post(client, "password-reset", {"email": email_of(user), "next": "/checkout"})

    assert response.status_code == 202
    assert len(mail.outbox) == 1
    message, html = sent_message()
    assert message.to == [email_of(user)]
    assert "/password-reset/confirm/" in message.body
    assert f"/password-reset/confirm/{uid_of(user)}/" in message.body
    assert "next=%2Fcheckout" in message.body
    assert f"/password-reset/confirm/{uid_of(user)}/" in html
    assert "<!DOCTYPE html>" in html


def test_password_reset_email_link_uses_frontend_url(
    client: Client,
    settings: Any,
) -> None:
    #   Bug real: o link saía com um FRONTEND_URL desatualizado (ex.: apontando para uma
    #   porta/origem que não está mais no ar), inacessível para quem recebe o e-mail.
    settings.FRONTEND_URL = "https://shop.example.com"
    user = make_user()

    post(client, "password-reset", {"email": email_of(user)})

    message, html = sent_message()
    assert f"https://shop.example.com/password-reset/confirm/{uid_of(user)}/" in message.body
    assert f"https://shop.example.com/password-reset/confirm/{uid_of(user)}/" in html


def test_password_reset_request_does_not_reveal_unknown_emails(client: Client) -> None:
    response = post(client, "password-reset", {"email": "ghost@example.com"})

    assert response.status_code == 202
    assert response.json() == {}
    assert not mail.outbox


def test_password_reset_request_validates_the_email_format(client: Client) -> None:
    response = post(client, "password-reset", {"email": "nope"})

    assert response.status_code == 400
    assert response.json()["email"]


def reset_link(user: UserModel) -> tuple[str, str]:
    return uid_of(user), default_token_generator.make_token(user)


def test_password_reset_validate(client: Client) -> None:
    user = make_user()
    uid, token = reset_link(user)

    assert post(client, "password-reset/validate", {"uid": uid, "token": token}).status_code == 200
    invalid = post(client, "password-reset/validate", {"uid": uid, "token": "bad"})
    assert invalid.status_code == 400
    assert invalid.json()["code"] == "invalid_link"


def test_password_reset_confirm_changes_the_password_and_burns_the_link(client: Client) -> None:
    user = make_user()
    uid, token = reset_link(user)

    response = post(
        client,
        "password-reset/confirm",
        {"uid": uid, "token": token, "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.check_password(NEW_PASSWORD)
    assert (
        post(client, "login", {"email": email_of(user), "password": NEW_PASSWORD}).status_code
        == 200
    )

    again = post(
        client,
        "password-reset/confirm",
        {
            "uid": uid,
            "token": token,
            "new_password1": "Yet-An0ther#One",
            "new_password2": "Yet-An0ther#One",
        },
    )
    assert again.status_code == 400
    assert again.json()["code"] == "invalid_link"


@pytest.mark.parametrize(
    ("password1", "password2"),
    [(NEW_PASSWORD, "different"), ("12345678", "12345678"), ("", "")],
)
def test_password_reset_confirm_field_errors(
    client: Client, password1: str, password2: str
) -> None:
    user = make_user()
    uid, token = reset_link(user)

    response = post(
        client,
        "password-reset/confirm",
        {"uid": uid, "token": token, "new_password1": password1, "new_password2": password2},
    )

    body = response.json()
    assert response.status_code == 400
    assert body.get("new_password1") or body.get("new_password2")
    assert "code" not in body
    user.refresh_from_db()
    assert user.check_password(PASSWORD)


def test_password_reset_confirm_with_invalid_link(client: Client) -> None:
    user = make_user()

    response = post(
        client,
        "password-reset/confirm",
        {
            "uid": uid_of(user),
            "token": "invalid",
            "new_password1": NEW_PASSWORD,
            "new_password2": NEW_PASSWORD,
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_link"


# ---------------------------------------------------------- django admin (is_staff)


def test_anonymous_user_cannot_reach_the_admin() -> None:
    #   Segurança real: continua sendo o próprio Django Admin, não o React, quem decide isto.
    response = Client().get("/admin/", follow=False)

    assert response.status_code in (302, 403)


def test_regular_authenticated_user_cannot_reach_the_admin(client: Client) -> None:
    client.force_login(make_user(is_staff=False))

    response = client.get("/admin/", follow=False)

    assert response.status_code in (302, 403)


def test_staff_user_can_reach_the_admin(client: Client) -> None:
    client.force_login(make_user(is_staff=True, is_superuser=True))

    response = client.get("/admin/", follow=False)

    assert response.status_code == 200
