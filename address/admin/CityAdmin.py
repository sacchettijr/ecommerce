from typing import TYPE_CHECKING

from django.contrib import admin

from address.forms import CityForm
from address.models import CityModel

if TYPE_CHECKING:
    BaseCityAdmin = admin.ModelAdmin[CityModel]
else:
    BaseCityAdmin = admin.ModelAdmin


@admin.register(CityModel)
class CityAdmin(BaseCityAdmin):
    form = CityForm

    list_display = (
        "id",
        "name",
        "state",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "state__name",
    )

    list_filter = (
        "state",
        "created_at",
        "updated_at",
    )
