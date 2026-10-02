from django.utils.http import url_has_allowed_host_and_scheme


def safe_next_path(
    value: str | None,
) -> str:

    if not value or not value.startswith("/") or value.startswith("//") or "\\" in value:
        return ""

    if not url_has_allowed_host_and_scheme(
        url=value,
        allowed_hosts=None,
    ):
        return ""

    return value
