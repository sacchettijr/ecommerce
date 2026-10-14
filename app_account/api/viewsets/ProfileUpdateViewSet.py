from typing import cast

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from app_account.api.form_errors import form_errors_payload
from app_account.api.request_data import request_data
from app_account.api.serialize_user import serialize_user
from app_account.forms import UserUpdateForm
from app_account.models import UserModel


class ProfileUpdateViewSet(
    viewsets.ViewSet,
):
    #   Uses the project's default IsAuthenticated permission (no AllowAny override): only an
    #   authenticated session can reach this. UserUpdateForm is always bound to request.user —
    #   no user identifier is ever accepted from the request, so a client cannot edit another
    #   account's profile. UserUpdateForm.Meta.fields only lists name/date_birth/phone, so any
    #   other submitted key (is_staff, is_superuser, ...) is simply ignored by the form.

    def create(
        self,
        request: Request,
    ) -> Response:
        user = cast(UserModel, request.user)
        form = UserUpdateForm(
            instance=user,
            data=request_data(request),
        )

        if not form.is_valid():
            return Response(
                data=form_errors_payload(form),
                status=status.HTTP_400_BAD_REQUEST,
            )

        #   Skips the write entirely when nothing actually changed.
        if form.has_changed():
            form.save()

        return Response(
            data={"user": serialize_user(user)},
        )
