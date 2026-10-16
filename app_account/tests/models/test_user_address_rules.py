from typing import Any, cast

import pytest
from django.db import IntegrityError, connection, transaction
from django.forms import inlineformset_factory

from app_account.forms import UserAddressBaseForm
from app_account.models import UserAddressModel, UserModel
from app_account.tests.factories import UserAddressFactory, UserFactory
from app_address.tests.factories import CityFactory

pytestmark = pytest.mark.django_db


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def add(user: UserModel, **kwargs: object) -> UserAddressModel:
    return cast(UserAddressModel, UserAddressFactory(user=user, **kwargs))


def primaries(user: UserModel) -> list[int]:
    return list(
        UserAddressModel.objects.filter(user=user, primary=True).values_list("pk", flat=True),
    )


def is_primary(address: UserAddressModel) -> bool:
    return cast(bool, UserAddressModel.objects.get(pk=address.pk).primary)


# ---------------------------------------------------------- primary (create)


def test_the_first_address_is_automatically_primary() -> None:
    user = make_user()

    first = add(user, primary=False)

    assert is_primary(first) is True


def test_the_first_address_is_primary_even_when_explicitly_submitted_as_not_primary() -> None:
    user = make_user()

    first = add(user, primary=False)

    assert primaries(user) == [first.pk]


def test_a_second_address_does_not_become_primary_automatically() -> None:
    user = make_user()
    first = add(user)

    second = add(user, primary=False)

    assert is_primary(second) is False
    assert primaries(user) == [first.pk]


def test_a_second_address_created_as_primary_unmarks_the_first_one() -> None:
    user = make_user()
    first = add(user)

    second = add(user, primary=True)

    assert primaries(user) == [second.pk]
    assert is_primary(first) is False


def test_first_address_rule_is_independent_per_user() -> None:
    user_1, user_2 = make_user(), make_user()

    first_of_1 = add(user_1)
    first_of_2 = add(user_2)

    assert primaries(user_1) == [first_of_1.pk]
    assert primaries(user_2) == [first_of_2.pk]


# ---------------------------------------------------------- primary (update)


def test_marking_another_address_as_primary_unmarks_the_previous_one() -> None:
    user = make_user()
    first = add(user)
    second = add(user)
    third = add(user)

    third.primary = True
    third.save()

    assert primaries(user) == [third.pk]
    assert is_primary(first) is False
    assert is_primary(second) is False


def test_primary_of_other_users_is_untouched() -> None:
    user_1, user_2 = make_user(), make_user()
    address_1 = add(user_1)
    address_2 = add(user_2)

    other = add(user_1, primary=True)

    assert primaries(user_1) == [other.pk]
    assert primaries(user_2) == [address_2.pk]
    assert is_primary(address_1) is False


# ---------------------------------------------------------- delete


def test_deleting_the_primary_promotes_the_oldest_remaining_address() -> None:
    user = make_user()
    first = add(user)
    second = add(user)

    first.delete()

    assert primaries(user) == [second.pk]


def test_deleting_a_non_primary_address_keeps_the_primary() -> None:
    user = make_user()
    first = add(user)
    second = add(user)

    second.delete()

    assert primaries(user) == [first.pk]


def test_deleting_the_only_address_leaves_the_user_without_addresses() -> None:
    user = make_user()
    only = add(user)

    only.delete()

    assert UserAddressModel.objects.filter(user=user).count() == 0
    assert primaries(user) == []


def test_queryset_delete_of_the_primary_also_promotes_another() -> None:
    user = make_user()
    first = add(user)
    second = add(user)

    UserAddressModel.objects.filter(pk=first.pk).delete()

    assert primaries(user) == [second.pk]


def test_deleting_a_user_cascades_without_errors() -> None:
    user = make_user()
    add(user)
    add(user)

    user.delete()

    assert UserAddressModel.objects.count() == 0


# ---------------------------------------------------------- database constraint


def test_database_rejects_two_primaries_written_around_the_model() -> None:
    user = make_user()
    add(user, primary=True)
    second = add(user)

    with pytest.raises(IntegrityError), transaction.atomic():
        UserAddressModel.objects.filter(pk=second.pk).update(primary=True)


def test_invariants_hold_after_the_operations_are_committed() -> None:
    user = make_user()
    for _ in range(4):
        add(user, primary=True)

    connection.check_constraints()

    assert len(primaries(user)) == 1
    assert UserAddressModel.objects.filter(user=user).count() == 4


# ---------------------------------------------------------- admin (inline formset)


def address_formset_class(extra: int) -> Any:
    return inlineformset_factory(
        UserModel,
        UserAddressModel,
        form=UserAddressBaseForm,
        fk_name="user",
        fields=(
            "primary",
            "street",
            "number",
            "complement",
            "reference",
            "district",
            "postal_code",
            "country",
            "state",
            "city",
        ),
        extra=extra,
    )


def formset_data(rows: list[dict[str, Any]], initial: int) -> dict[str, Any]:
    prefix = "user_addresses"
    data: dict[str, Any] = {
        f"{prefix}-TOTAL_FORMS": str(len(rows)),
        f"{prefix}-INITIAL_FORMS": str(initial),
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }
    for index, row in enumerate(rows):
        for key, value in row.items():
            data[f"{prefix}-{index}-{key}"] = value
    return data


def row_from(address: UserAddressModel, **overrides: Any) -> dict[str, Any]:
    #   Resubmits the address's own current field values unchanged - matches what a
    #   real admin round-trip sends for a row the administrator didn't touch, so
    #   form.has_changed() is correctly False for it and save() isn't re-triggered
    #   with a blank "primary" checkbox overwriting a promotion from a sibling row's
    #   deletion. A fresh/unrelated fake row (base_row()) would make every row look
    #   "changed", which isn't realistic and isn't what these tests are about.
    address_any = cast(Any, address)
    row: dict[str, Any] = {
        "id": address.pk,
        "street": address.street,
        "number": address.number,
        "complement": address.complement,
        "reference": address.reference,
        "district": address.district,
        "postal_code": address.postal_code,
        "country": address_any.country_id,
        "state": address_any.state_id,
        "city": address_any.city_id,
    }
    row.update(overrides)
    return row


def base_row(**overrides: Any) -> dict[str, Any]:
    city = cast(Any, CityFactory())
    row: dict[str, Any] = {
        "street": "Main St",
        "number": "123",
        "complement": "",
        "reference": "",
        "district": "Downtown",
        "postal_code": "00000-000",
        "country": city.state.country_id,
        "state": city.state_id,
        "city": city.pk,
    }
    row.update(overrides)
    return row


def test_formset_deleting_the_primary_and_its_replacement_in_the_same_submission() -> None:
    user = make_user()
    first = add(user, primary=True)
    second = add(user)
    third = add(user)

    data = formset_data(
        [
            row_from(first, DELETE="on"),
            row_from(second, DELETE="on"),
            row_from(third),
        ],
        initial=3,
    )
    formset = address_formset_class(extra=0)(data, {}, instance=user, prefix="user_addresses")

    assert formset.is_valid(), formset.errors
    with transaction.atomic():
        formset.save()

    connection.check_constraints()
    assert UserAddressModel.objects.filter(pk__in=[first.pk, second.pk]).exists() is False
    #   Only "third" survives: it must end up primary, never a deleted row.
    assert primaries(user) == [third.pk]


def test_formset_operations_do_not_affect_another_users_addresses() -> None:
    user_1, user_2 = make_user(), make_user()
    first = add(user_1, primary=True)
    second = add(user_1)
    other = add(user_2, primary=True)

    data = formset_data(
        [
            row_from(first, DELETE="on"),
            row_from(second),
        ],
        initial=2,
    )
    formset = address_formset_class(extra=0)(data, {}, instance=user_1, prefix="user_addresses")

    assert formset.is_valid(), formset.errors
    with transaction.atomic():
        formset.save()

    assert primaries(user_1) == [second.pk]
    assert primaries(user_2) == [other.pk]
    assert is_primary(other) is True
