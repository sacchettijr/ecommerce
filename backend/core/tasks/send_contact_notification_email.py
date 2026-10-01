import logging
from typing import Any

from celery import (
    shared_task,
)
from django.conf import (
    settings,
)
from django.utils import (
    translation,
)
from django.utils.translation import (
    gettext_lazy as _,
)

from utils.email import send_html_email

logger = logging.getLogger(
    name=__name__,
)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_contact_notification_email(
    self: Any,
    *,
    name: str,
    email: str,
    phone: str,
    message: str,
    site_name: str,
    language: str,
) -> None:
    try:
        with translation.override(
            language=language,
        ):
            send_html_email(
                subject=f"[Contato site] {name}",
                template_name="email/email_contact.html",
                context={
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "message": message,
                    "site_name": site_name,
                },
                to=[
                    settings.DEFAULT_FROM_EMAIL,
                ],
                text_content=("You have received a new message through the contact form."),
            )
    except Exception as exc:
        logger.exception(
            _(message="Error sending contact email (attempt %s)"),
            self.request.retries,
        )
        raise self.retry(exc=exc) from exc
