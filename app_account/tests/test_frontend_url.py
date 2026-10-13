import pytest
from django.test import override_settings

from utils.frontend_url import frontend_scheme_and_domain


@pytest.mark.parametrize(
    ("frontend_url", "expected"),
    [
        #   Dev atrás do Nginx: tudo publicado em "localhost" (porta 80, implícita).
        ("http://localhost", ("http", "localhost")),
        #   Dev sem o Nginx, direto no Vite.
        ("http://localhost:5173", ("http", "localhost:5173")),
        #   Produção: domínio real e HTTPS, sem depender de "localhost" nem de qualquer porta.
        ("https://shop.example.com", ("https", "shop.example.com")),
    ],
)
def test_frontend_scheme_and_domain_uses_frontend_url(
    frontend_url: str,
    expected: tuple[str, str],
) -> None:
    with override_settings(FRONTEND_URL=frontend_url):
        assert frontend_scheme_and_domain() == expected
