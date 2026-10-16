from typing import (
    Any,
    cast,
)

from django import forms
from django.forms.models import ModelChoiceIteratorValue

from app_address.models import StateModel


class StateLocationSelect(forms.Select):
    #   Stamps each state <option> with its country (data-country), the same way
    #   CityLocationSelect stamps city options with state/country, so the
    #   state -> country autofill works from the very first page load, not only
    #   after a state list has been rebuilt by the cascading JS. Needs the field's
    #   queryset to use select_related("country") — see UserAddressBaseForm.
    class Media:
        js = ("src/js/admin/city_location_select.js",)

    def create_option(
        self,
        name: str,
        value: Any,
        label: int | str,
        selected: bool,
        index: int,
        subindex: int | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if isinstance(value, ModelChoiceIteratorValue):
            #   .instance isn't in django-stubs, even though it's real public Django API
            #   (since 3.1, added specifically for this use case).
            state = cast(StateModel, cast(Any, value).instance)
            option["attrs"]["data-country"] = cast(Any, state).country_id

        return option
