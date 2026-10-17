import math
import time
from typing import cast

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle


def get_client_identifier(request: Request) -> str:
    """Stable per-client key for rate limiting: the authenticated user's own pk, or the
    request's IP otherwise. Reuses BaseThrottle.get_ident() (NUM_PROXIES-aware) instead of
    re-implementing IP extraction — a client can never pick its own identifier.
    """
    user = request.user

    if user.is_authenticated:
        return f"user:{user.pk}"

    ip = BaseThrottle().get_ident(request)
    return f"ip:{ip}"


def seconds_until_next_allowed(key: str, interval_seconds: int) -> int | None:
    """Atomically allows (and records) an action under `key`, unless the caller already
    performed one within the last `interval_seconds`.

    Uses cache.add() — a single set-if-not-exists round trip — as the atomic primitive:
    whichever concurrent caller reaches the cache first "wins" the window, with no
    separate check-then-write race. The cached value is the "next allowed at" timestamp
    itself (not relied-upon key TTL introspection, since Django's generic cache API has no
    portable way to read a key's remaining TTL across backends).

    Returns None if the action is now allowed (and has just been recorded). Returns the
    whole number of seconds remaining before the next attempt will be allowed, otherwise.
    """
    next_allowed_at = time.time() + interval_seconds

    if cache.add(key, next_allowed_at, timeout=interval_seconds):
        return None

    stored = cast("float | None", cache.get(key))

    if stored is None:
        #   Expired in the gap between our failed add() and this read — safe to record a
        #   fresh marker now and allow this request.
        cache.add(key, time.time() + interval_seconds, timeout=interval_seconds)
        return None

    remaining = stored - time.time()
    return max(1, math.ceil(remaining)) if remaining > 0 else None
