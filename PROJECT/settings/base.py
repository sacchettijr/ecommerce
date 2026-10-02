from pathlib import Path

from dotenv import load_dotenv

# =========================================================
#   BASE
# =========================================================


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


# =========================================================
#   URLS
# =========================================================


ROOT_URLCONF = "PROJECT.urls"


# =========================================================
#   SERVERS
# =========================================================


WSGI_APPLICATION = "PROJECT.wsgi.application"
