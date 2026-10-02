import pytest
from django.test import override_settings

from utils.site_url import public_scheme_and_domain


@pytest.mark.parametrize(
    ("site_url", "frontend_url", "expected"),
    [
        #   Dev: o Nginx publica o site em "localhost" (porta 80, implícita); o Vite continua
        #   em ":5173" só para FRONTEND_URL (CORS), e não deve aparecer em nenhum link de e-mail.
        ("http://localhost", "http://localhost:5173", ("http", "localhost")),
        #   Produção: domínio real e HTTPS, sem depender de "localhost" nem de qualquer porta.
        ("https://shop.example.com", "https://shop.example.com", ("https", "shop.example.com")),
    ],
)
def test_public_scheme_and_domain_uses_site_url_not_frontend_url(
    site_url: str,
    frontend_url: str,
    expected: tuple[str, str],
) -> None:
    with override_settings(SITE_URL=site_url, FRONTEND_URL=frontend_url):
        assert public_scheme_and_domain() == expected
