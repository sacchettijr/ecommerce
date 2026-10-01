from typing import cast

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from account.api.form_errors import form_errors_payload
from account.api.get_user_from_uid import get_user_from_uid
from account.api.mixins import PublicAuthViewSet
from account.api.request_data import request_data
from account.api.serializers import UidTokenSerializer
from account.emails import send_verification_email
from account.forms import ResendVerificationEmailForm
from account.models import UserModel
from account.tokens import email_verification_token
from utils.redirect import safe_next_path


class EmailVerificationViewSet(
    PublicAuthViewSet,
):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "token_check"

    @action(
        detail=False,
        methods=["post"],
        url_path="confirm",
    )
    def confirm(
        self,
        request: Request,
    ) -> Response:
        serializer = UidTokenSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        user = get_user_from_uid(
            uid=serializer.validated_data["uid"],
        )

        #   Token inválido, expirado ou já utilizado não se distinguem: o Django os trata igual
        #   (o hash inclui is_email_verified), e o fluxo antigo tinha uma única mensagem.
        if user is None or not email_verification_token.check_token(
            user,
            serializer.validated_data["token"],
        ):
            return Response(
                data={"code": "invalid_link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_email_verified = True
        user.save(
            update_fields=["is_email_verified"],
        )

        return Response(
            data={},
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="resend",
        throttle_scope="email_verification",
    )
    def resend(
        self,
        request: Request,
    ) -> Response:
        data = request_data(request)
        form = ResendVerificationEmailForm(
            data=data,
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = UserModel.objects.filter(
            email=form.cleaned_data["email"],
            is_active=True,
            is_email_verified=False,
        ).first()

        #   Resposta idêntica exista ou não a conta: não revela quais e-mails estão cadastrados.
        if user is not None:
            send_verification_email(
                user=user,
                next_path=safe_next_path(cast(str | None, data.get("next"))),
            )

        return Response(
            data={},
            status=status.HTTP_202_ACCEPTED,
        )
