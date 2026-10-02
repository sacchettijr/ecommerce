# =========================================================
#   MIDDLEWARE
# =========================================================


MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    #   Serve os arquivos estáticos coletados; precisa vir logo após o SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    #   CORS: precisa vir antes de qualquer middleware que gere resposta
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #   TRANSLATION
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    #   AUTO RELOAD WHEN SAVING
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    #   MIDDLEWARE TO GET THE LOGGED-IN USER
    "account.middleware.CurrentUserMiddleware",
]
