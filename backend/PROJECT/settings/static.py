import os

from .base import BASE_DIR
from .security import DEBUG

# =========================================================
#   STATICFILES
# =========================================================


STATIC_URL = "static/"

STATICFILES_DIRS: list[str] = [
    os.path.join(
        BASE_DIR,
        "static",
    ),
]


STATIC_ROOT: str = os.path.join(
    BASE_DIR,
    "staticfiles",
)

if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "utils.whitenoise_storage.LenientManifestStaticFilesStorage",
        },
    }
