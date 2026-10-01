from typing import TYPE_CHECKING

from django.contrib import admin

from address.forms import StateForm
from address.models import StateModel

if TYPE_CHECKING:
    BaseStateAdmin = admin.ModelAdmin[StateModel]
else:
    BaseStateAdmin = admin.ModelAdmin


@admin.register(StateModel)
class StateAdmin(BaseStateAdmin):
    form = StateForm

    list_display = (
        "id",
        "name",
        "code",
        "country",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "code",
        "country__name",
    )

    list_filter = (
        "country",
        "created_at",
        "updated_at",
    )
