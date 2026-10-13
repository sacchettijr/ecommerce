from typing import cast

from django.contrib.auth import login
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from app_account.api.form_errors import form_errors_payload
from app_account.api.mixins import PublicAuthViewSet
from app_account.api.request_data import request_data
from app_account.api.serialize_user import serialize_user
from app_account.forms import LoginForm
from app_account.models import UserModel


class LoginViewSet(
    PublicAuthViewSet,
):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "login"

    def create(
        self,
        request: Request,
    ) -> Response:
        #   O LoginForm (AuthenticationForm) continua sendo a fonte das regras e mensagens:
        #   credenciais inválidas, conta desativada e e-mail não confirmado.
        data = request_data(request)
        form = LoginForm(
            request=request,
            data={
                "username": data.get("email", ""),
                "password": data.get("password", ""),
            },
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(
                    form,
                    rename={"username": "email"},
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = cast(UserModel, form.get_user())

        login(
            request=request,
            user=user,
        )

        return Response(
            data={"user": serialize_user(user)},
        )
