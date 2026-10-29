from typing import cast

import pytest
from django.contrib import admin

from app_address.admin.CityAdmin import CityAdmin
from app_address.admin.CountryAdmin import CountryAdmin
from app_address.admin.StateAdmin import StateAdmin
from app_address.forms import CityForm, CountryForm, StateForm
from app_address.models import CityModel, CountryModel, StateModel

pytestmark = pytest.mark.django_db


def test_country_admin_configuration_is_unchanged() -> None:
    country_admin = cast(CountryAdmin, admin.site._registry[CountryModel])

    assert country_admin.form is CountryForm
    assert country_admin.list_display == ("id", "name", "iso_code", "created_at")
    assert country_admin.list_display_links == ("id", "name")
    assert country_admin.search_fields == ("name", "iso_code")
    assert country_admin.list_filter == ("created_at", "updated_at")


def test_state_admin_configuration_is_unchanged() -> None:
    state_admin = cast(StateAdmin, admin.site._registry[StateModel])

    assert state_admin.form is StateForm
    assert state_admin.list_display == ("id", "name", "code", "country", "created_at")
    assert state_admin.list_display_links == ("id", "name")
    assert state_admin.search_fields == ("name", "code", "country__name")
    assert state_admin.list_filter == ("country", "created_at", "updated_at")


def test_city_admin_configuration_is_unchanged() -> None:
    city_admin = cast(CityAdmin, admin.site._registry[CityModel])

    assert city_admin.form is CityForm
    assert city_admin.list_display == ("id", "name", "state", "created_at")
    assert city_admin.list_display_links == ("id", "name")
    assert city_admin.search_fields == ("name", "state__name")
    assert city_admin.list_filter == ("state", "created_at", "updated_at")
