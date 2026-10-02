import logging
from collections.abc import (
    Mapping,
)
from typing import (
    Any,
)

from celery import (
    shared_task,
)
from django.template import (
    loader,
)
from django.utils import (
    translation,
)
from django.utils.translation import (
    gettext_lazy as _,
)

from account.models import (
    UserModel,
)
from utils.email import (
    send_html_email,
)

logger = logging.getLogger(
    name=__name__,
)

SUBJECT_TEMPLATE_NAME = "email/email_verification_subject.txt"
TEXT_TEMPLATE_NAME = "email/email_verification_email.txt"
HTML_TEMPLATE_NAME = "email/email_verification_email.html"


#   Nome explícito: send_verification_email envia a tarefa por este nome (sem importá-la),
#   e o nome automático do Celery seria "<módulo>.<função>" e não seria reconhecido pelo worker.
@shared_task(
    name="account.tasks.send_email_verification_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_email_verification_email(
    self: Any,
    *,
    user_id: int,
    domain: str,
    site_name: str,
    uid: str,
    token: str,
    protocol: str,
    to_email: str,
    language: str,
    next_path: str = "",
) -> None:

    try:
        user = UserModel.objects.get(pk=user_id)
    except UserModel.DoesNotExist:
        return

    try:
        with translation.override(
            language=language,
        ):
            full_context: Mapping[str, object] = {
                "user": user,
                "domain": domain,
                "site_name": site_name,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "next": next_path,
            }

            rendered_subject = loader.render_to_string(
                template_name=SUBJECT_TEMPLATE_NAME,
                context=full_context,
            )

            subject: str = "".join(
                rendered_subject.splitlines(),
            )

            text_content = loader.render_to_string(
                template_name=TEXT_TEMPLATE_NAME,
                context=full_context,
            )

            send_html_email(
                subject=subject,
                template_name=HTML_TEMPLATE_NAME,
                context=full_context,
                to=[
                    to_email,
                ],
                text_content=text_content,
            )
    except Exception as exc:
        logger.exception(
            _(
                message="Error sending registration confirmation email (attempt %s).",
            ),
            self.request.retries,
        )
        raise self.retry(exc=exc) from exc
