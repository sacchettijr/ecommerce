import os

from celery import Celery

os.environ.setdefault(
    key="DJANGO_SETTINGS_MODULE",
    value="PROJECT.settings",
)

# =========================================================
#   CELERY
# =========================================================


app: Celery = Celery(
    main="PROJECT",
)

app.config_from_object(
    obj="django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()
