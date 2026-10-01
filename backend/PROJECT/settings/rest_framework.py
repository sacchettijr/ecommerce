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
    "DEFAULT_PAGINATION_CLASS": "core.api.pagination.StandardPagination",
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
        "token_check": "60/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
