from urllib.parse import urlsplit

from django.conf import settings


def public_scheme_and_domain() -> tuple[str, str]:
    #   SITE_URL é o endereço público do site (o que a pessoa digita/clica), servido pelo Nginx.
    #   Não usar FRONTEND_URL aqui: em desenvolvimento ele aponta para o Vite (":5173"), que só
    #   existe dentro da rede Docker e nunca deveria ir num link de e-mail.
    parts = urlsplit(
        url=str(
            settings.SITE_URL,
        )
    )

    return str(parts.scheme), str(parts.netloc)
