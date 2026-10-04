from .templates import FRONTEND_URL

# =========================================================
#   CORS
# =========================================================


CORS_ALLOWED_ORIGINS: list[str] = [
    FRONTEND_URL,
]

CORS_ALLOW_CREDENTIALS = True
