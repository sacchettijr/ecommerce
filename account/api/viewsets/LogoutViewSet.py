from django.contrib.auth import logout
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from account.api.mixins import PublicAuthViewSet


class LogoutViewSet(
    PublicAuthViewSet,
):
    def create(
        self,
        request: Request,
    ) -> Response:
        logout(
            request=request,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
