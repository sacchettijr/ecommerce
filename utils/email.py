from collections.abc import (
    Mapping,
    Sequence,
)

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.safestring import SafeString


def send_html_email(
    *,
    subject: str,
    template_name: str,
    context: Mapping[str, object] | None = None,
    to: Sequence[str],
    reply_to: Sequence[str] | None = None,
    text_content: str | None = None,
) -> None:

    html_content: SafeString = render_to_string(
        template_name,
        context=context or {},
    )

    email: EmailMultiAlternatives = EmailMultiAlternatives(
        subject=subject,
        body=text_content or "",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list[str](to),
        reply_to=list[str](reply_to or []),
    )

    email.attach_alternative(
        content=html_content,
        mimetype="text/html",
    )

    email.send()
