from django.urls import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
