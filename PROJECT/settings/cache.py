from dotenv import load_dotenv

from utils.env import (
    env,
    env_bool,
    env_int,
)

# =========================================================
#   CACHE (Redis)
# =========================================================

load_dotenv()


ON_RENDER: bool = env_bool(
    name="RENDER",
    default=False,
)

CACHES: dict[str, dict[str, str]] = {
    "default": (
        {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
        if ON_RENDER
        else {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": (
                f"redis://{env(name='REDIS_HOST')}:"
                f"{env_int(name='REDIS_PORT', default=6379)}"
                f"/{env_int(name='REDIS_CACHE_DB', default=1)}"
            ),
        }
    ),
    "debug-toolbar": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}
