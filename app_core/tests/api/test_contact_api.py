import time
from collections.abc import Iterator
from typing import Any, cast

import pytest
from django.core.cache import cache
from django.test import Client

from app_account.models import UserModel
from app_account.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

BASE = "/api/core/contact/"


@pytest.fixture(autouse=True)
def clean_throttle_cache() -> Iterator[None]:
    #   Throttle/cooldown counters live in the cache (Redis) — zero it so tests don't
    #   bleed into each other.
    cache.clear()
    yield
    cache.clear()


def payload(**overrides: Any) -> dict[str, Any]:
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+5511987654321",
        "message": "Hello, I would like more information about your products.",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------- basic validation


def test_valid_submission_is_accepted(client: Client) -> None:
    response = client.post(BASE, data=payload(), content_type="application/json")

    assert response.status_code == 202


def test_invalid_phone_is_rejected(client: Client) -> None:
    response = client.post(
        BASE,
        data=payload(phone="not-a-phone-number"),
        content_type="application/json",
    )

    assert response.status_code == 400


def test_a_single_word_name_is_rejected(client: Client) -> None:
    response = client.post(
        BASE,
        data=payload(name="Maria"),
        content_type="application/json",
    )

    body = response.json()
    assert response.status_code == 400
    assert body["name"]


def test_a_full_name_with_first_and_last_name_is_accepted(client: Client) -> None:
    response = client.post(
        BASE,
        data=payload(name="Maria Eduarda"),
        content_type="application/json",
    )

    assert response.status_code == 202


def test_invalid_submission_does_not_consume_the_cooldown(client: Client) -> None:
    client.post(BASE, data=payload(phone="not-a-phone-number"), content_type="application/json")

    response = client.post(BASE, data=payload(), content_type="application/json")

    assert response.status_code == 202


# ---------------------------------------------------------- 60s cooldown


def test_second_valid_submission_within_60s_is_blocked(client: Client) -> None:
    first = client.post(BASE, data=payload(), content_type="application/json")
    second = client.post(BASE, data=payload(), content_type="application/json")

    assert first.status_code == 202
    assert second.status_code == 429


def test_blocked_response_has_a_stable_code_and_retry_after(client: Client) -> None:
    client.post(BASE, data=payload(), content_type="application/json")

    response = client.post(BASE, data=payload(), content_type="application/json")

    body = response.json()
    assert body["code"] == "contact_cooldown"
    assert isinstance(body["retry_after"], int)
    assert 1 <= body["retry_after"] <= 60
    assert response.headers["Retry-After"] == str(body["retry_after"])


def test_allowed_again_once_the_cooldown_elapses(client: Client) -> None:
    client.post(BASE, data=payload(), content_type="application/json")
    #   Simulates the 60s window having already elapsed, instead of a real sleep.
    cache.set("contact_cooldown:ip:127.0.0.1", time.time() - 1, timeout=60)

    response = client.post(BASE, data=payload(), content_type="application/json")

    assert response.status_code == 202


def test_two_different_ips_have_independent_cooldowns(client: Client) -> None:
    first = client.post(
        BASE,
        data=payload(),
        content_type="application/json",
        REMOTE_ADDR="203.0.113.10",
    )
    second = client.post(
        BASE,
        data=payload(),
        content_type="application/json",
        REMOTE_ADDR="203.0.113.20",
    )

    assert first.status_code == 202
    assert second.status_code == 202


def test_authenticated_users_have_independent_cooldowns_from_each_other(client: Client) -> None:
    user_a = cast(UserModel, UserFactory())
    user_b = cast(UserModel, UserFactory())

    client.force_login(user_a)
    first = client.post(BASE, data=payload(), content_type="application/json")
    client.logout()

    client.force_login(user_b)
    second = client.post(BASE, data=payload(), content_type="application/json")

    assert first.status_code == 202
    assert second.status_code == 202


# ---------------------------------------------------------- existing 5/hour cap preserved


def test_the_existing_hourly_cap_still_applies_independently_of_the_new_cooldown(
    client: Client,
) -> None:
    #   Satisfy the new 60s cooldown for every attempt by advancing the stored marker into
    #   the past right before each one, isolating this test to the *other*, pre-existing
    #   mechanism (ScopedRateThrottle, "5/hour") rather than re-testing the new cooldown.
    key = "contact_cooldown:ip:127.0.0.1"

    for _ in range(5):
        cache.delete(key)
        response = client.post(BASE, data=payload(), content_type="application/json")
        assert response.status_code == 202

    cache.delete(key)
    blocked = client.post(BASE, data=payload(), content_type="application/json")

    assert blocked.status_code == 429
    #   The hourly throttle is DRF's own unmodified mechanism — its own default code.
    assert blocked.json()["code"] == "throttled"
