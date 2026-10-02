from .templates import FRONTEND_URL

# =========================================================
#   PASSWORD VALIDATION
# =========================================================


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================================================
#   AUTHENTICATION
# =========================================================


LOGIN_URL: str = f"{FRONTEND_URL}/login/"
LOGIN_REDIRECT_URL: str = f"{FRONTEND_URL}/account/"
LOGOUT_REDIRECT_URL: str = f"{FRONTEND_URL}/"
AUTH_USER_MODEL = "account.UserModel"

AUTHENTICATION_BACKENDS: list[str] = [
    "guardian.backends.ObjectPermissionBackend",
    "account.backends.EmailVerifiedModelBackend.EmailVerifiedModelBackend",
]


# =========================================================
#   GUARDIAN
# =========================================================


ANONYMOUS_USER_NAME = None
