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

from .StateModel import StateModel


class CityModel(BaseModel):
    name = models.CharField(
        verbose_name=_(
            message="Name",
        ),
        max_length=250,
    )

    state = models.ForeignKey(
        to=StateModel,
        verbose_name=_(
            message="State/Province",
        ),
        on_delete=models.PROTECT,
        related_name="cities",
    )

    class Meta:
        db_table = "city"
        verbose_name = _(message="City")
        verbose_name_plural = _(message="Cities")

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
