from utils.env import env_int

# =========================================================
#   DJANGO REST FRAMEWORK
# =========================================================


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "app_core.api.pagination.StandardPagination",
    "PAGE_SIZE": env_int(
        name="PAGE_SIZE",
        default=25,
    ),
    "DEFAULT_THROTTLE_RATES": {
        "contact": "5/hour",
        "login": "10/minute",
        "signup": "10/hour",
        "email_verification": "5/hour",
        "password_reset": "5/hour",
        "password_change": "10/hour",
        "token_check": "60/hour",
    },
    #   Nginx is always the sole proxy in front of Django (local and in the one real
    #   deployment — see nginx/nginx.conf), and it honestly sets
    #   X-Forwarded-For $proxy_add_x_forwarded_for on every proxied location. Without this,
    #   BaseThrottle.get_ident() falls back to REMOTE_ADDR, which behind nginx is nginx's
    #   own container IP for every request — silently sharing every IP-based throttle
    #   across all anonymous visitors. With NUM_PROXIES=1, get_ident() takes the *last*
    #   entry of X-Forwarded-For (the one nginx itself appended), ignoring anything a
    #   client might have pre-pended.
    "NUM_PROXIES": 1,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
