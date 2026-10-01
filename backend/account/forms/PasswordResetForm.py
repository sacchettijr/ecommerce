from typing import Any

from django.conf import settings
from django.contrib.auth.forms import (
    PasswordResetForm as DjangoPasswordResetForm,
)
from django.utils import translation

from account.tasks import send_password_reset_email
from utils.dispatch_task import dispatch_task


class PasswordResetForm(DjangoPasswordResetForm):
    def send_mail(
        self,
        subject_template_name: str,
        email_template_name: str,
        context: dict[Any, Any],
        from_email: str | None,
        to_email: str,
        html_email_template_name: str | None = None,
    ) -> None:
        dispatch_task(
            lambda: send_password_reset_email.delay(
                user_id=context["user"].pk,
                subject_template_name=subject_template_name,
                text_template_name=email_template_name,
                html_template_name=html_email_template_name,
                context={
                    "email": context["email"],
                    "domain": context["domain"],
                    "site_name": context["site_name"],
                    "uid": context["uid"],
                    "token": context["token"],
                    "protocol": context["protocol"],
                    "next": context.get("next", ""),
                },
                to_email=to_email,
                language=translation.get_language() or settings.LANGUAGE_CODE,
            ),
            description="account.tasks.send_password_reset_email",
        )
