from typing import Any

from rest_framework.request import Request


def request_data(
    request: Request,
) -> dict[str, Any]:

    data = request.data

    return data if isinstance(data, dict) else {}
