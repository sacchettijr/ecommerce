from typing import TYPE_CHECKING

from django.contrib import admin

from address.forms import CountryForm
from address.models import CountryModel

if TYPE_CHECKING:
    BaseCountryAdmin = admin.ModelAdmin[CountryModel]
else:
    BaseCountryAdmin = admin.ModelAdmin


@admin.register(CountryModel)
class CountryAdmin(BaseCountryAdmin):
    form = CountryForm

    list_display = (
        "id",
        "name",
        "iso_code",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "iso_code",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )
