from typing import Any

from django.http.request import HttpRequest

from product.models import (
    ProductCategoryModel,
)


def context_processors_product_categories(request: HttpRequest) -> dict[str, Any]:
    return {
        "product_categories": ProductCategoryModel.objects.filter(
            active=True,
        )
    }
