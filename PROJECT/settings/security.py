import os

import django_stubs_ext

from utils.env import (
    env,
    env_bool,
    env_list,
)

# =========================================================
#   SEGURANÇA
# =========================================================
SECRET_KEY: str = env(
    name="SECRET_KEY",
)


DEBUG: bool = env_bool(
    name="DEBUG",
    default=False,
)

ALLOWED_HOSTS: list[str] = env_list(
    name="ALLOWED_HOSTS",
    default=[
        "localhost",
    ],
)


RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS: list[str] = env_list(
    name="CSRF_TRUSTED_ORIGINS",
    default=[],
)

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

if DEBUG:
    django_stubs_ext.monkeypatch()
