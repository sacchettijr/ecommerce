from typing import (
    Any,
    cast,
)

from django import forms
from django.forms.models import ModelChoiceIteratorValue

from app_address.models import CityModel


class CityLocationSelect(forms.Select):
    #   Anota cada <option> da cidade com o estado/país correspondentes
    #   (data-state/data-country), para o JS preencher os campos de estado e país
    #   automaticamente quando a cidade é escolhida. Precisa que o queryset do campo
    #   use select_related("state__country") — ver UserAddressBaseForm.
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
            #   .instance não está nos stubs do django-stubs, embora seja parte da API
            #   pública real do Django (desde a 3.1, criada justamente para este caso).
            city = cast(CityModel, cast(Any, value).instance)
            option["attrs"]["data-state"] = cast(Any, city).state_id
            option["attrs"]["data-country"] = cast(Any, city.state).country_id

        return option
