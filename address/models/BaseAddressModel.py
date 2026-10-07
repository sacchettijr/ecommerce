from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.translation import (
    gettext_lazy as _,
)

from core.models import BaseModel

from .CityModel import CityModel
from .CountryModel import CountryModel
from .StateModel import StateModel


class BaseAddressModel(BaseModel):
    street: models.CharField[str, str] = models.CharField(
        verbose_name=_(
            message="Street",
        ),
        max_length=255,
    )
    number: models.CharField[str, str] = models.CharField(
        verbose_name=_(
            message="Number",
        ),
        max_length=20,
    )
    complement: models.CharField[str, str] = models.CharField(
        verbose_name=_(
            message="Complement",
        ),
        max_length=100,
        blank=True,
        help_text="Apartment, Block, Room, ...",
    )
    reference: models.CharField[str, str] = models.CharField(
        verbose_name=_(
            message="Reference",
        ),
        max_length=255,
        blank=True,
        help_text="Example: Near the Central Market",
    )
    district: models.CharField[str, str] = models.CharField(
        max_length=100,
        verbose_name=_(
            message="District",
        ),
    )
    postal_code: models.CharField[str, str] = models.CharField(
        verbose_name=_(
            message="Postal code",
        ),
        max_length=20,
    )
    city: ForeignKey[CityModel, CityModel] = models.ForeignKey(
        verbose_name=_(
            message="City",
        ),
        to=CityModel,
        related_name="%(class)s_addresses",
        on_delete=models.PROTECT,
    )
    state: ForeignKey[StateModel, StateModel] = models.ForeignKey(
        verbose_name=_(
            message="State/Province",
        ),
        to=StateModel,
        related_name="%(class)s_addresses",
        on_delete=models.PROTECT,
    )
    country: ForeignKey[CountryModel, CountryModel] = models.ForeignKey(
        verbose_name=_(
            message="Country",
        ),
        to=CountryModel,
        related_name="%(class)s_addresses",
        on_delete=models.PROTECT,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.street}, {self.number} - {self.district}"
