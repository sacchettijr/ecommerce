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

from .CountryModel import CountryModel


class StateModel(BaseModel):
    name = models.CharField(
        verbose_name=_(
            message="Name",
        ),
        max_length=250,
    )
    code = models.CharField(
        #   Administrative code
        verbose_name=_(
            message="Code",
        ),
        max_length=2,
        validators=[
            validate_alpha,
        ],
        blank=True,
    )
    country = models.ForeignKey(
        to=CountryModel,
        verbose_name=_(
            message="Country",
        ),
        on_delete=models.PROTECT,
        related_name="states",
    )

    class Meta:
        db_table = "state"
        verbose_name = _(message="State/Province")
        verbose_name_plural = _(message="States/Provinces")

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
