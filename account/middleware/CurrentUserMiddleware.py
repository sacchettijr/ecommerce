from collections.abc import Callable
from typing import cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.http import (
    HttpRequest,
    HttpResponse,
)

from utils.current_user import set_current_user


class CurrentUserMiddleware:
    def __init__(
        self,
        get_response: Callable[
            [HttpRequest],
            HttpResponse,
        ],
    ) -> None:
        self.get_response = get_response

    def __call__(
        self,
        request: HttpRequest,
    ) -> HttpResponse:

        user = request.user

        if user.is_authenticated:
            authenticated_user = cast(
                AbstractBaseUser,
                user,
            )
            set_current_user(user=authenticated_user)
        else:
            set_current_user(user=None)

        try:
            return self.get_response(request)
        finally:
            set_current_user(user=None)
