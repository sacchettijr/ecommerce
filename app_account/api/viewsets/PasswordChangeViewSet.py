from typing import cast

from django.contrib.auth import update_session_auth_hash
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from app_account.api.form_errors import form_errors_payload
from app_account.api.request_data import request_data
from app_account.forms import PasswordChangeForm
from app_account.models import UserModel


class PasswordChangeViewSet(
    viewsets.ViewSet,
):
    #   Uses the project's default IsAuthenticated permission (no AllowAny override): only an
    #   authenticated session can reach this. The form always operates on request.user — no
    #   user identifier is ever accepted from the request, so a client cannot target another
    #   account. SessionAuthentication enforces CSRF for this request automatically.
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "password_change"

    def create(
        self,
        request: Request,
    ) -> Response:
        #   IsAuthenticated guarantees request.user is a real UserModel by the time create()
        #   runs; the type checker can't see that permission-level guarantee on its own.
        form = PasswordChangeForm(
            cast(UserModel, request.user),
            data=request_data(request),
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        form.save()
        #   Keeps the current session valid after the password hash changes, instead of
        #   silently logging the user out mid-request.
        update_session_auth_hash(request, form.user)

        return Response(
            data={},
        )
