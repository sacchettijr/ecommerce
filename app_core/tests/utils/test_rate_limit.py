import threading
import time
from collections.abc import Iterator
from typing import Any, cast

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest
from django.test import RequestFactory

from app_account.models import UserModel
from app_account.tests.factories import UserFactory
from utils.rate_limit import get_client_identifier, seconds_until_next_allowed

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clean_cache() -> Iterator[None]:
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------- seconds_until_next_allowed


def test_first_call_is_allowed() -> None:
    assert seconds_until_next_allowed("k1", 60) is None


def test_immediate_second_call_is_blocked_with_the_full_interval_remaining() -> None:
    seconds_until_next_allowed("k2", 60)

    remaining = seconds_until_next_allowed("k2", 60)

    assert remaining is not None
    assert 1 <= remaining <= 60


def test_remaining_seconds_decreases_as_time_passes() -> None:
    key = "k3"
    now = time.time()
    #   Simulates "accepted 50 seconds ago" by writing the stored marker directly, instead
    #   of sleeping for real in the test.
    cache.set(key, now - 50 + 60, timeout=60)

    remaining = seconds_until_next_allowed(key, 60)

    assert remaining is not None
    assert remaining <= 10


def test_allowed_again_once_the_window_has_elapsed() -> None:
    key = "k4"
    #   A marker that already expired (its "next allowed at" is in the past).
    cache.set(key, time.time() - 1, timeout=60)

    assert seconds_until_next_allowed(key, 60) is None


def test_different_keys_are_independent() -> None:
    seconds_until_next_allowed("k5a", 60)

    assert seconds_until_next_allowed("k5b", 60) is None


def test_only_one_concurrent_caller_wins_the_window() -> None:
    key = "k6"
    results: list[int | None] = []
    lock = threading.Lock()

    def attempt() -> None:
        result = seconds_until_next_allowed(key, 60)
        with lock:
            results.append(result)

    threads = [threading.Thread(target=attempt) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    allowed = [r for r in results if r is None]
    blocked = [r for r in results if r is not None]
    assert len(allowed) == 1
    assert len(blocked) == 9


# ---------------------------------------------------------- get_client_identifier


def make_request(**meta: str) -> HttpRequest:
    factory = RequestFactory()
    request = factory.post("/api/core/contact/")
    request.META["REMOTE_ADDR"] = "203.0.113.5"
    request.META.update(meta)
    return request


def test_authenticated_request_is_identified_by_user_pk() -> None:
    user = cast(UserModel, UserFactory())
    request = cast(Any, make_request())
    request.user = user

    assert get_client_identifier(request) == f"user:{user.pk}"


def test_anonymous_request_is_identified_by_ip() -> None:
    request = cast(Any, make_request())
    request.user = AnonymousUser()

    assert get_client_identifier(request) == "ip:203.0.113.5"


def test_a_forged_leading_x_forwarded_for_entry_does_not_change_the_identity() -> None:
    #   NUM_PROXIES=1 means only the LAST entry (the one nginx itself appended) is
    #   trusted — a client-supplied first entry must be ignored.
    request = cast(
        Any,
        make_request(HTTP_X_FORWARDED_FOR="9.9.9.9, 203.0.113.5"),
    )
    request.user = AnonymousUser()

    assert get_client_identifier(request) == "ip:203.0.113.5"


def test_two_different_authenticated_users_are_independent() -> None:
    user_a = cast(UserModel, UserFactory())
    user_b = cast(UserModel, UserFactory())
    request_a = cast(Any, make_request())
    request_a.user = user_a
    request_b = cast(Any, make_request())
    request_b.user = user_b

    assert get_client_identifier(request_a) != get_client_identifier(request_b)
