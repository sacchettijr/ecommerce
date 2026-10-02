from utils.env import (
    env,
    env_bool,
    env_int,
)

# =========================================================
#   EMAIL
# =========================================================


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: str = env(name="EMAIL_HOST")
EMAIL_PORT: int = env_int(name="EMAIL_PORT", default=587)
EMAIL_USE_TLS: bool = env_bool(name="EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER: str = env(name="EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD: str = env(name="EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL: str = env(name="DEFAULT_FROM_EMAIL")
