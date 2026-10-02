from pathlib import Path

from dotenv import load_dotenv

# =========================================================
#   BASE
# =========================================================


BASE_DIR = Path(__file__).resolve().parent.parent.parent

#   .env lives at the repo root (one level above backend/), next to docker-compose.yml,
#   which reads it via "env_file". This path is only exercised when running manage.py
#   directly (outside Docker); Compose already injects the variables into the container.
load_dotenv(dotenv_path=BASE_DIR.parent / ".env")


# =========================================================
#   URLS
# =========================================================


ROOT_URLCONF = "PROJECT.urls"


# =========================================================
#   SERVERS
# =========================================================


WSGI_APPLICATION = "PROJECT.wsgi.application"
