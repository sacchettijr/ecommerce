from contextvars import ContextVar

from django.contrib.auth.base_user import AbstractBaseUser

_current_user: ContextVar[AbstractBaseUser | None] = ContextVar(
    "current_user",
    default=None,
)


def get_current_user() -> AbstractBaseUser | None:
    return _current_user.get()


def set_current_user(
    user: AbstractBaseUser | None,
) -> None:
    _current_user.set(user)
