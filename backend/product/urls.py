from django.urls import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

from product.api.viewsets import (
    ProductCategorySimpleListViewSet,
    ProductDetailViewSet,
    ProductSimpleListViewSet,
)

router = DefaultRouter()


router.register(
    prefix="products",
    viewset=ProductSimpleListViewSet,
    basename="product",
)
router.register(
    prefix="products",
    viewset=ProductDetailViewSet,
    basename="product_detail",
)
router.register(
    prefix="categories",
    viewset=ProductCategorySimpleListViewSet,
    basename="product_category",
)

urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
