from utils.env import env

from .base import BASE_DIR

# =========================================================
#   INTERNATIONALIZATION
# =========================================================


LANGUAGE_CODE: str = env(
    name="LANGUAGE_CODE",
    default="pt-br",
)

LANGUAGES = (
    ("pt-br", "Português"),
    ("en", "English"),
    ("es", "Español"),
)

LOCALE_PATHS = (BASE_DIR / "locale",)

TIME_ZONE: str = env(
    name="TIME_ZONE",
    default="America/Manaus",
)

USE_I18N = True

USE_TZ = True

PHONENUMBER_DEFAULT_REGION: str = env(
    name="PHONENUMBER_DEFAULT_REGION",
    default="BR",
)
