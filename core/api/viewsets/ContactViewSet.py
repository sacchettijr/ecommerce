from django.utils.translation import get_language
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from core.api.serializers import ContactSerializer
from core.tasks.send_contact_notification_email import send_contact_notification_email
from utils.dispatch_task import dispatch_task


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
            description="core.tasks.send_contact_notification_email",
        )

        return Response(
            data={},
            status=status.HTTP_202_ACCEPTED,
        )
