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

#   Endereço onde uma pessoa de fato acessa o React: é para onde apontam os links dos
#   e-mails (confirmação de cadastro, redefinição de senha), os links de produto/categoria
#   (ver get_absolute_url) e o CORS. Preencha com o que estiver realmente publicado — atrás
#   do Nginx normalmente é "http://localhost" (porta 80); testando sem o Nginx, direto no
#   Vite, é "http://localhost:5173"; em produção, o domínio real (HTTPS).
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

#   Nome do site usado nos e-mails.
SITE_NAME = os.getenv(
    "SITE_NAME",
    "E-Commerce",
)
