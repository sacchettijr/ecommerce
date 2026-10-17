from typing import Any, cast

from django.utils.translation import get_language
from django.utils.translation import gettext as _
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.exceptions import Throttled
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from app_core.api.serializers import ContactSerializer
from app_core.tasks.send_contact_notification_email import send_contact_notification_email
from utils.dispatch_task import dispatch_task
from utils.rate_limit import get_client_identifier, seconds_until_next_allowed

#   Seconds a client must wait between ACCEPTED sends (started only once the backend has
#   actually validated and dispatched a message, never on a rejected/invalid attempt).
#   Complements, not replaces, the existing 5/hour ScopedRateThrottle below: that one
#   counts request attempts in a sliding hourly window; this one tracks exact elapsed time
#   since the last accepted send, which the hourly counter's own averaged wait() math
#   can't express.
CONTACT_COOLDOWN_SECONDS = 60


class ContactViewSet(
    viewsets.ViewSet,
):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "contact"

    def create(
        self,
        request: Request,
    ) -> Response:
        serializer = ContactSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        #   Only reached once validation succeeds — an invalid submission never starts or
        #   consumes the cooldown.
        cooldown_key = f"contact_cooldown:{get_client_identifier(request)}"
        remaining = seconds_until_next_allowed(
            key=cooldown_key,
            interval_seconds=CONTACT_COOLDOWN_SECONDS,
        )

        if remaining is not None:
            raise Throttled(
                wait=remaining,
                code="contact_cooldown",
            )

        data = serializer.validated_data

        dispatch_task(
            lambda: send_contact_notification_email.delay(
                name=data["name"],
                email=data["email"],
                phone=str(data["phone"]),
                message=data["message"],
                site_name="E-Commerce",
                language=get_language() or "pt-br",
            ),
            description="app_core.tasks.send_contact_notification_email",
        )

        return Response(
            data={},
            status=status.HTTP_202_ACCEPTED,
        )

    def handle_exception(
        self,
        exc: Exception,
    ) -> Response:
        #   Unifies the response shape for BOTH throttle mechanisms (the automatic 5/hour
        #   ScopedRateThrottle and the manual cooldown above) into this project's own
        #   stable-code error convention (see api.md), rather than DRF's default bare
        #   {"detail": "..."} — the frontend needs a reliable numeric retry_after and a
        #   stable code regardless of which limit fired.
        if isinstance(exc, Throttled) and cast(Any, exc).wait is not None:
            wait = cast(int, cast(Any, exc).wait)
            code = cast(str, exc.get_codes())

            return Response(
                data={
                    "code": code,
                    "detail": _("Please wait %(seconds)s seconds before sending another message.")
                    % {"seconds": wait},
                    "retry_after": wait,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(wait)},
            )

        return super().handle_exception(exc)
