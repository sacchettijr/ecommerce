# =========================================================
#   APLICAÇÕES
# =========================================================


INSTALLED_APPS = [
    #   DJANGO
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #   DEV
    "django_browser_reload",
    #   LIBS
    "corsheaders",
    "phonenumber_field",
    "rest_framework",
    "django_filters",
    "guardian",
    "drf_spectacular",
    #   APPS
    "core",
    "account",
    "product",
    "address",
]
