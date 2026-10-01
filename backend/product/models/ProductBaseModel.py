from typing import (
    Any,
    cast,
)

from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)
from django.utils.translation import (
    pgettext_lazy,
)

from core.models import BaseModel
from utils.slug import generate_unique_slug


class ProductBaseModel(BaseModel):
    active = models.BooleanField(
        #   Com contexto: o msgid "Active" puro colide com catálogos de terceiros (admin, guardian),
        #   que o traduzem como "Ação".
        verbose_name=pgettext_lazy(
            context="product status",
            message="Active",
        ),
        default=True,
    )
    name = models.CharField(
        verbose_name=_(
            message="Name",
        ),
        max_length=500,
    )
    slug = models.SlugField(
        verbose_name=_(
            message="Slug",
        ),
        max_length=500,
        unique=True,
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ("pk",)

    def __str__(self) -> str:
        name = cast(
            str,
            self.name,
        )
        return name

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        name = cast(
            str,
            self.name,
        )

        self.slug = generate_unique_slug(
            instance=self,
            value=name,
        )
        return super().save(*args, **kwargs)
