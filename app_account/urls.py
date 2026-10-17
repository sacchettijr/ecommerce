from django.urls import (
    URLPattern,
    URLResolver,
)
from rest_framework.routers import DefaultRouter

from app_account.api.viewsets import (
    EmailVerificationViewSet,
    LoginViewSet,
    LogoutViewSet,
    PasswordChangeViewSet,
    PasswordResetViewSet,
    ProfileUpdateViewSet,
    PublicWishlistViewSet,
    SessionViewSet,
    SignUpViewSet,
    UserAddressViewSet,
    WishlistItemViewSet,
)

router = DefaultRouter()

router.register(
    prefix="session",
    viewset=SessionViewSet,
    basename="session",
)
router.register(
    prefix="login",
    viewset=LoginViewSet,
    basename="login",
)
router.register(
    prefix="logout",
    viewset=LogoutViewSet,
    basename="logout",
)
router.register(
    prefix="signup",
    viewset=SignUpViewSet,
    basename="signup",
)
router.register(
    prefix="email-verification",
    viewset=EmailVerificationViewSet,
    basename="email_verification",
)
router.register(
    prefix="password-reset",
    viewset=PasswordResetViewSet,
    basename="password_reset",
)
router.register(
    prefix="password-change",
    viewset=PasswordChangeViewSet,
    basename="password_change",
)
router.register(
    prefix="profile",
    viewset=ProfileUpdateViewSet,
    basename="profile_update",
)
router.register(
    prefix="addresses",
    viewset=UserAddressViewSet,
    basename="user_address",
)
router.register(
    prefix="wishlist",
    viewset=WishlistItemViewSet,
    basename="wishlist_item",
)
router.register(
    prefix="wishlist/public",
    viewset=PublicWishlistViewSet,
    basename="wishlist_public",
)

urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
