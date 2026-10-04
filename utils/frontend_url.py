from urllib.parse import urlsplit

from django.conf import settings


def frontend_scheme_and_domain() -> tuple[str, str]:
    #   FRONTEND_URL é o único endereço "onde o React está publicado": usado tanto para
    #   montar links de e-mail (confirmação de cadastro, redefinição de senha) quanto para
    #   get_absolute_url() de produto/categoria. Configure-o para bater com o que estiver
    #   realmente acessível no ambiente atual (ver comentário em settings/templates.py).
    parts = urlsplit(
        url=str(
            settings.FRONTEND_URL,
        )
    )

    return str(parts.scheme), str(parts.netloc)
