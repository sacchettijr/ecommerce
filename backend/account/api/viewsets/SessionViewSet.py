from typing import Any

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from account.api.serialize_user import serialize_user
from account.models import UserModel


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionViewSet(
    viewsets.ViewSet,
):
    #   Usuário da sessão atual (ou null). Também entrega o cookie CSRF ao React.
    permission_classes = (AllowAny,)

    def list(
        self,
        request: Request,
    ) -> Response:
        user = request.user
        payload: dict[str, Any] | None = (
            serialize_user(user) if isinstance(user, UserModel) else None
        )

        return Response(
            data={"user": payload},
        )
