from django.contrib.auth.models import BaseUserManager

#   DANGER: normalize_name does the same thing as normalize_whitespace.


def normalize_whitespace(
    name: str,
) -> str:
    #   Remove duplicate spaces
    return " ".join(
        name.split(),
    )


def normalize_email(
    email: str,
) -> str:
    #   Set email address to Django's format and force lowercase letters
    return BaseUserManager.normalize_email(
        email=email.strip(),
    ).lower()
