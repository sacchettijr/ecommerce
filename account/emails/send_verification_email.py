from typing import cast

from celery import current_app
from django.conf import settings
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.models import UserModel
from account.tokens import email_verification_token
from utils.dispatch_task import dispatch_task
from utils.frontend_url import frontend_scheme_and_domain


def send_verification_email(
    user: UserModel,
    next_path: str = "",
) -> None:

    EMAIL_VERIFICATION_TASK = "account.tasks.send_email_verification_email"

    #   O link do e-mail abre a página React de confirmação (FRONTEND_URL).
    scheme, domain = frontend_scheme_and_domain()

    dispatch_task(
        action=lambda: current_app.send_task(
            name=EMAIL_VERIFICATION_TASK,
            kwargs={
                "user_id": user.pk,
                "domain": domain,
                "site_name": settings.SITE_NAME,
                "uid": urlsafe_base64_encode(
                    s=force_bytes(
                        s=user.pk,
                    ),
                ),
                "token": email_verification_token.make_token(user),
                "protocol": scheme,
                "to_email": cast(
                    str,
                    user.email,
                ),
                "language": translation.get_language() or settings.LANGUAGE_CODE,
                "next_path": next_path,
            },
        ),
        description="account.tasks.send_email_verification_email",
    )
