from typing import cast

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from account.api.form_errors import form_errors_payload
from account.api.mixins import PublicAuthViewSet
from account.api.request_data import request_data
from account.emails import send_verification_email
from account.forms import SignUpForm
from utils.redirect import safe_next_path


class SignUpViewSet(
    PublicAuthViewSet,
):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "signup"

    def create(
        self,
        request: Request,
    ) -> Response:
        data = request_data(request)
        form = SignUpForm(
            data=data,
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = form.save()

        #   O e-mail de confirmação é enviado pelo Django (Celery); o React só mostra o resultado.
        send_verification_email(
            user=user,
            next_path=safe_next_path(cast(str | None, data.get("next"))),
        )

        return Response(
            data={},
            status=status.HTTP_201_CREATED,
        )
