from django.urls import (
    URLPattern,
    URLResolver,
)
from rest_framework.routers import DefaultRouter

from account.api.viewsets import (
    EmailVerificationViewSet,
    LoginViewSet,
    LogoutViewSet,
    PasswordResetViewSet,
    SessionViewSet,
    SignUpViewSet,
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

urlpatterns: list[URLPattern | URLResolver] = [
    *router.urls,
]
