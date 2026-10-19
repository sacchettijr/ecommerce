from utils.env import env

from .base import BASE_DIR

# =========================================================
#   INTERNATIONALIZATION
# =========================================================


LANGUAGE_CODE: str = env(
    name="LANGUAGE_CODE",
    default="en",
)

LANGUAGES = (
    ("pt-br", "Português"),
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("it", "Italiano"),
)

LOCALE_PATHS = (BASE_DIR / "locale",)

TIME_ZONE: str = env(
    name="TIME_ZONE",
    default="America/New_York",
)

USE_I18N = True

USE_TZ = True

PHONENUMBER_DEFAULT_REGION: str = env(
    name="PHONENUMBER_DEFAULT_REGION",
    default="BR",
)
