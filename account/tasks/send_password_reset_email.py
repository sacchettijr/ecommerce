import logging
from typing import (
    Any,
)

from celery import (
    shared_task,
)
from django.template import (
    loader,
)
from django.utils import translation
from django.utils.translation import (
    gettext_lazy as _,
)

from account.models import (
    UserModel,
)
from utils.email import send_html_email

logger = logging.getLogger(name=__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_password_reset_email(
    self: Any,
    *,
    user_id: int,
    subject_template_name: str,
    text_template_name: str,
    html_template_name: str | None,
    context: dict[str, Any],
    to_email: str,
    language: str,
) -> None:

    try:
        user = UserModel.objects.get(pk=user_id)
    except UserModel.DoesNotExist:
        return

    try:
        with translation.override(
            language=language,
        ):
            full_context = {
                **context,
                "user": user,
            }

            rendered_subject = loader.render_to_string(
                template_name=subject_template_name,
                context=full_context,
            )

            subject: str = "".join(
                rendered_subject.splitlines(),
            )

            text_content = loader.render_to_string(
                template_name=text_template_name,
                context=full_context,
            )

            send_html_email(
                subject=subject,
                template_name=html_template_name or text_template_name,
                context=full_context,
                to=[
                    to_email,
                ],
                text_content=text_content,
            )
    except Exception as exc:
        logger.exception(
            _(
                message="Error sending password reset email (attempt %s).",
            ),
            self.request.retries,
        )
        raise self.retry(exc=exc) from exc
