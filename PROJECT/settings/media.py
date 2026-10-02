import os

from .base import BASE_DIR

# =========================================================
#   MEDIA
# =========================================================


MEDIA_URL = "media/"

MEDIA_ROOT: str = os.path.join(
    BASE_DIR,
    "mediafiles",
)
