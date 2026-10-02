import os

from .base import BASE_DIR

# =========================================================
#   TEMPLATES
# =========================================================


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        #   The React app (frontend/) is a separate project, sibling of backend/ — Django
        #   never renders its templates. Only the email templates below are used.
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

#   Endereço público do site, servido pelo Nginx: é para onde apontam os links dos e-mails
#   (confirmação de e-mail, redefinição de senha). Em produção, é o domínio real (HTTPS).
#   Não confundir com FRONTEND_URL, que é o endereço interno do Vite, usado só pelo CORS.
SITE_URL = os.getenv(
    "SITE_URL",
    "http://localhost",
)

#   Nome do site usado nos e-mails.
SITE_NAME = os.getenv(
    "SITE_NAME",
    "E-Commerce",
)
