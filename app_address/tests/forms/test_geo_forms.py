from typing import Any, cast

import pytest

from app_address.forms import CityForm, CountryForm, StateForm
from app_address.tests.factories import CountryFactory, StateFactory

pytestmark = pytest.mark.django_db


# ------------------------------------------------------------------ CountryForm


def test_country_form_accepts_a_valid_name_and_iso_code() -> None:
    form = CountryForm(data={"name": "Brazil", "iso_code": "BR"})

    assert form.is_valid(), form.errors


def test_country_form_rejects_a_name_shorter_than_three_characters() -> None:
    form = CountryForm(data={"name": "Br", "iso_code": "BR"})

    assert not form.is_valid()
    assert "name" in form.errors


def test_country_form_collapses_internal_whitespace_in_the_name() -> None:
    form = CountryForm(data={"name": "United   States", "iso_code": "US"})

    assert form.is_valid(), form.errors
    assert form.cleaned_data["name"] == "United States"


# -------------------------------------------------------------------- StateForm


def test_state_form_accepts_a_valid_submission() -> None:
    country = cast(Any, CountryFactory())

    form = StateForm(data={"name": "California", "code": "CA", "country": country.pk})

    assert form.is_valid(), form.errors


def test_state_form_rejects_a_name_shorter_than_three_characters() -> None:
    country = cast(Any, CountryFactory())

    form = StateForm(data={"name": "CA", "code": "CA", "country": country.pk})

    assert not form.is_valid()
    assert "name" in form.errors


def test_state_form_rejects_a_non_alphabetic_code() -> None:
    country = cast(Any, CountryFactory())

    form = StateForm(data={"name": "California", "code": "1A", "country": country.pk})

    assert not form.is_valid()
    assert "code" in form.errors


# --------------------------------------------------------------------- CityForm


def test_city_form_accepts_a_valid_submission() -> None:
    state = cast(Any, StateFactory())

    form = CityForm(data={"name": "Los Angeles", "state": state.pk})

    assert form.is_valid(), form.errors


def test_city_form_rejects_a_name_shorter_than_three_characters() -> None:
    state = cast(Any, StateFactory())

    form = CityForm(data={"name": "LA", "state": state.pk})

    assert not form.is_valid()
    assert "name" in form.errors
