from typing import Any

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS


def form_errors_payload(
    form: forms.Form,
    *,
    rename: dict[str, str] | None = None,
) -> dict[str, Any]:

    rename = rename or {}
    data = form.errors.get_json_data()
    payload: dict[str, Any] = {}

    for field, errors in data.items():
        key = "non_field_errors" if field == NON_FIELD_ERRORS else rename.get(field, field)
        payload[key] = [error["message"] for error in errors]

    general = data.get(NON_FIELD_ERRORS)

    if general:
        payload["code"] = general[0]["code"]

    return payload
