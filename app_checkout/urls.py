from django.urls import (
    URLPattern,
    URLResolver,
)
from rest_framework.routers import DefaultRouter

from app_checkout.api.viewsets import CartItemViewSet

router = DefaultRouter()
router.register(
    prefix="items",
    viewset=CartItemViewSet,
    basename="cart_item",
)


urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
