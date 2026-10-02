import os
from typing import (
    Any,
    cast,
)

import dj_database_url

from utils.env import (
    env,
)

# =========================================================
#   DATABASE
# =========================================================


def _default_database() -> dict[str, Any]:

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return cast(
            dict[str, Any],
            dj_database_url.parse(
                url=database_url,
                conn_max_age=600,
                conn_health_checks=True,
            ),
        )

    return {
        "ENGINE": env(
            name="POSTGRES_ENGINE",
            default="django.db.backends.postgresql",
        ),
        "NAME": env(name="POSTGRES_DB"),
        "USER": env(name="POSTGRES_USER"),
        "PASSWORD": env(name="POSTGRES_PASSWORD"),
        "HOST": env(name="POSTGRES_HOST"),
        "PORT": env(name="POSTGRES_PORT"),
    }


DATABASES = {
    "default": _default_database(),
}
