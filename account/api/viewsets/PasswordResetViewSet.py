from typing import cast

from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
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
from account.forms import PasswordResetForm
from account.models import UserModel
from utils.frontend_url import frontend_scheme_and_domain
from utils.redirect import safe_next_path

INVALID_LINK = {"code": "invalid_link"}


class PasswordResetViewSet(
    PublicAuthViewSet,
):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "token_check"

    def __get_valid_user(
        self,
        request: Request,
    ) -> UserModel | None:
        serializer = UidTokenSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        user = get_user_from_uid(
            uid=serializer.validated_data["uid"],
        )

        if user is None or not default_token_generator.check_token(
            user,
            serializer.validated_data["token"],
        ):
            return None

        return user

    def create(
        self,
        request: Request,
    ) -> Response:
        data = request_data(request)
        form = PasswordResetForm(
            data=data,
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        scheme, domain = frontend_scheme_and_domain()

        #   O e-mail (Celery) aponta para a página React de confirmação (FRONTEND_URL).
        #   A resposta é a mesma exista ou não a conta, como no fluxo antigo.
        form.save(
            request=request,
            domain_override=domain,
            use_https=scheme == "https",
            email_template_name="email/email_password_reset.txt",
            subject_template_name="email/email_password_reset_subject.txt",
            html_email_template_name="email/email_password_reset.html",
            extra_email_context={
                "site_name": settings.SITE_NAME,
                "next": safe_next_path(cast(str | None, data.get("next"))),
            },
        )

        return Response(
            data={},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="validate",
    )
    def validate(
        self,
        request: Request,
    ) -> Response:
        if self.__get_valid_user(request) is None:
            return Response(
                data=INVALID_LINK,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            data={},
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="confirm",
    )
    def confirm(
        self,
        request: Request,
    ) -> Response:
        user = self.__get_valid_user(request)

        if user is None:
            return Response(
                data=INVALID_LINK,
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = SetPasswordForm(
            user=user,
            data=request_data(request),
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        form.save()

        return Response(
            data={},
        )
