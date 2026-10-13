from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.views.decorators.http import require_GET


@require_GET
def api_health_check(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        data={
            "status": "ok",
        },
    )
