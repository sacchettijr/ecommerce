from .templates import (
    FRONTEND_URL,
    SITE_URL,
)

# =========================================================
#   CORS
# =========================================================


CORS_ALLOWED_ORIGINS: list[str] = [
    FRONTEND_URL,
    SITE_URL,
]
