from django.http import HttpRequest

from utils.env import env_list

from .apps import INSTALLED_APPS
from .middleware import MIDDLEWARE
from .security import DEBUG
from .test import TESTING

# =========================================================
#   FERRAMENTAS DE DESENVOLVIMENTO (fora dos testes e fora de produção)
# =========================================================


if DEBUG and not TESTING:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(
        MIDDLEWARE.index("corsheaders.middleware.CorsMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
else:
    INSTALLED_APPS.remove("django_browser_reload")
    MIDDLEWARE.remove("django_browser_reload.middleware.BrowserReloadMiddleware")


INTERNAL_IPS: list[str] = env_list(
    name="INTERNAL_IP",
    default=[
        "127.0.0.1",
    ],
)


def show_toolbar(
    request: HttpRequest,
) -> bool:

    return DEBUG


DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.community.CommunityPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "PROJECT.settings.debug_toolbar.show_toolbar",
    "TOOLBAR_STORE_CLASS": "debug_toolbar.store.CacheStore",
    "CACHE_BACKEND": "debug-toolbar",
}
