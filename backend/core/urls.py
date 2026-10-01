from django.urls import (
    URLPattern,
    URLResolver,
    path,
)
from rest_framework.routers import DefaultRouter

from core.api.viewsets import ContactViewSet

from .views import api_health_check

router = DefaultRouter()

router.register(
    prefix="contact",
    viewset=ContactViewSet,
    basename="contact",
)

urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
    path(
        route="health/",
        view=api_health_check,
        name="url_api_health_check",
    ),
]
