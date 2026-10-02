from typing import (
    Any,
    cast,
)

from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)

from core.models import BaseModel
from utils.normalize import normalize_whitespace
from utils.validator import validate_alpha


class CountryModel(BaseModel):
    name = models.CharField(
        verbose_name=_(
            message="Name",
        ),
        max_length=250,
    )
    iso_code = models.CharField(
        #   ISO 3166-1 alpha-2
        verbose_name=_(
            message="ISO code",
        ),
        max_length=2,
        validators=[
            validate_alpha,
        ],
    )

    class Meta:
        db_table = "country"
        verbose_name = _(message="Country")
        verbose_name_plural = _(message="Countries")

    def __str__(self) -> str:
        return cast(str, self.name)

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        name = cast(str, self.name)
        self.name = normalize_whitespace(name=name)

        return super().save(*args, **kwargs)
