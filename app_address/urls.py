from django.urls import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

from app_address.api.viewsets import (
    CityListViewSet,
    StateListViewSet,
)

router = DefaultRouter()


router.register(
    prefix="states",
    viewset=StateListViewSet,
    basename="state",
)
router.register(
    prefix="cities",
    viewset=CityListViewSet,
    basename="city",
)

urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
