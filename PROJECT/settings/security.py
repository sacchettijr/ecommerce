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

#   O Nginx sempre fica na frente do Django (local e em produção) e manda esse header
#   dizendo se a conexão original do navegador era HTTPS. Sem confiar nele aqui, o
#   Django usa o esquema da conexão INTERNA (nginx -> Django, sempre HTTP simples) para
#   montar URLs absolutas (ex.: campos de imagem da API) — sempre "http://", mesmo
#   quando a página foi carregada via "https://". Isso não força HTTPS nem mexe em
#   cookies; só corrige o esquema usado ao montar URLs. Por isso fica fora do "if not
#   DEBUG": mesmo em modo de prototipação, o Nginx já está na frente com HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

if DEBUG:
    django_stubs_ext.monkeypatch()
