from decimal import Decimal
from typing import (
    Any,
)

from django.core.exceptions import ValidationError
from django.utils.translation import (
    gettext_lazy as _,
)


class NormalizedProductPriceFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_price(self) -> Decimal:
        price = self.cleaned_data["price"]

        if price <= 0:
            raise ValidationError(
                message=_(
                    message="The price must be greater than zero.",
                ),
            )

        return price
