from datetime import datetime
from typing import cast

import pytest
from django.db import IntegrityError, connection, transaction

from app_account.forms import UserWishlistItemCreateForm
from app_account.models import (
    UserModel,
    UserWishlistItemModel,
    UserWishlistModel,
)
from app_account.tests.factories import (
    UserFactory,
    UserWishlistItemFactory,
)
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db


def make_user() -> UserModel:
    return cast(UserModel, UserFactory())


def wishlist_of(user: UserModel) -> UserWishlistModel:
    return UserWishlistModel.objects.get(user=user)


def make_product() -> ProductModel:
    return cast(ProductModel, ProductFactory())


def add(
    wishlist: UserWishlistModel,
    product: ProductModel | None = None,
) -> UserWishlistItemModel:
    return cast(
        UserWishlistItemModel,
        UserWishlistItemFactory(
            wishlist=wishlist,
            product=product or make_product(),
        ),
    )


def positions(wishlist: UserWishlistModel) -> list[int]:
    return list(
        UserWishlistItemModel.objects.filter(
            wishlist=wishlist,
        ).values_list(
            "position",
            flat=True,
        ),
    )


def ids_in_order(wishlist: UserWishlistModel) -> list[int]:
    return list(
        UserWishlistItemModel.objects.filter(
            wishlist=wishlist,
        ).values_list(
            "pk",
            flat=True,
        ),
    )


def position_of(item: UserWishlistItemModel) -> int:
    return cast(
        int,
        UserWishlistItemModel.objects.get(
            pk=item.pk,
        ).position,
    )


# ---------------------------------------------------------- inclusion


def test_adding_an_item_associates_it_with_the_wishlist_and_product() -> None:
    user = make_user()
    wishlist = wishlist_of(user)
    product = make_product()

    item = add(wishlist, product)

    assert item.wishlist == wishlist
    assert item.product == product


def test_adding_several_products_to_the_same_wishlist() -> None:
    wishlist = wishlist_of(
        user=make_user(),
    )

    add(wishlist)
    add(wishlist)
    add(wishlist)

    assert (
        UserWishlistItemModel.objects.filter(
            wishlist=wishlist,
        ).count()
        == 3
    )


def test_the_same_product_can_be_in_different_users_wishlists() -> None:
    wishlist_1, wishlist_2 = wishlist_of(make_user()), wishlist_of(make_user())
    product = make_product()

    add(wishlist_1, product)
    add(wishlist_2, product)

    assert UserWishlistItemModel.objects.filter(product=product).count() == 2


def test_added_at_is_set_automatically() -> None:
    item = add(wishlist_of(make_user()))

    assert cast("datetime", item.added_at) is not None


# ---------------------------------------------------------- duplicate product


def test_adding_the_same_product_twice_to_the_same_wishlist_is_rejected_by_the_database() -> None:
    wishlist = wishlist_of(make_user())
    product = make_product()
    add(wishlist, product)

    with pytest.raises(IntegrityError), transaction.atomic():
        UserWishlistItemModel.objects.create(wishlist=wishlist, product=product)


def test_form_reports_a_clear_error_for_a_duplicated_product() -> None:
    wishlist = wishlist_of(make_user())
    product = make_product()
    add(wishlist, product)

    form = UserWishlistItemCreateForm(
        data={"wishlist": wishlist.pk, "product": product.pk},
    )

    assert form.is_valid() is False
    assert form.non_field_errors()


def test_form_accepts_the_same_product_for_a_different_wishlist() -> None:
    wishlist_1 = wishlist_of(make_user())
    wishlist_2 = wishlist_of(make_user())
    product = make_product()
    add(wishlist_1, product)

    form = UserWishlistItemCreateForm(
        data={"wishlist": wishlist_2.pk, "product": product.pk},
    )

    assert form.is_valid() is True


# ---------------------------------------------------------- position (create)


def test_first_item_gets_position_zero() -> None:
    wishlist = wishlist_of(make_user())

    item = add(wishlist)

    assert position_of(item) == 0


def test_new_items_are_always_appended_to_the_end() -> None:
    wishlist = wishlist_of(make_user())

    first = add(wishlist)
    second = add(wishlist)
    third = add(wishlist)

    assert ids_in_order(wishlist) == [first.pk, second.pk, third.pk]
    assert positions(wishlist) == [0, 1, 2]


def test_positions_are_independent_per_wishlist() -> None:
    wishlist_1, wishlist_2 = (
        wishlist_of(
            user=make_user(),
        ),
        wishlist_of(
            user=make_user(),
        ),
    )
    add(wishlist=wishlist_1)
    add(wishlist=wishlist_1)
    before = positions(
        wishlist=wishlist_2,
    )

    add(wishlist=wishlist_1)
    add(wishlist=wishlist_2)

    assert positions(
        wishlist=wishlist_1,
    ) == [0, 1, 2]
    assert positions(
        wishlist=wishlist_2,
    ) == [*before, len(before)]


# ---------------------------------------------------------- position (reorganization)


def test_moving_an_item_to_the_front() -> None:
    wishlist = wishlist_of(
        user=make_user(),
    )
    a, b, c = add(wishlist), add(wishlist), add(wishlist)

    c.position = 0
    c.save()

    assert ids_in_order(wishlist) == [c.pk, a.pk, b.pk]
    assert positions(wishlist) == [0, 1, 2]


def test_moving_an_item_to_the_middle() -> None:
    wishlist = wishlist_of(
        user=make_user(),
    )
    items = [add(wishlist) for _ in range(5)]

    items[4].position = 1
    items[4].save()

    expected = [items[0].pk, items[4].pk, items[1].pk, items[2].pk, items[3].pk]
    assert ids_in_order(wishlist) == expected
    assert positions(wishlist) == [
        0,
        1,
        2,
        3,
        4,
    ]


def test_moving_an_item_past_the_end_normalizes_to_the_last_position() -> None:
    wishlist = wishlist_of(
        user=make_user(),
    )
    a, b, c = add(wishlist), add(wishlist), add(wishlist)

    a.position = 99
    a.save()

    assert ids_in_order(wishlist) == [
        b.pk,
        c.pk,
        a.pk,
    ]
    assert positions(wishlist) == [0, 1, 2]


def test_reorganizing_one_wishlist_does_not_affect_another() -> None:
    wishlist_1, wishlist_2 = (
        wishlist_of(
            user=make_user(),
        ),
        wishlist_of(
            user=make_user(),
        ),
    )
    a, b = (
        add(
            wishlist=wishlist_1,
        ),
        add(
            wishlist=wishlist_1,
        ),
    )
    other = add(
        wishlist=wishlist_2,
    )

    b.position = 0
    b.save()

    assert ids_in_order(
        wishlist=wishlist_1,
    ) == [b.pk, a.pk]
    assert positions(
        wishlist=wishlist_2,
    ) == [0]
    assert (
        position_of(
            item=other,
        )
        == 0
    )


def test_deleting_the_middle_item_closes_the_position_gap() -> None:
    wishlist = wishlist_of(user=make_user())
    a, b, c = add(wishlist), add(wishlist), add(wishlist)

    b.delete()

    assert ids_in_order(wishlist) == [a.pk, c.pk]
    assert positions(wishlist) == [0, 1]


def test_moving_an_item_to_another_wishlist_closes_the_gap_in_the_origin() -> None:
    wishlist_1, wishlist_2 = wishlist_of(user=make_user()), wishlist_of(user=make_user())
    a, b, c = (
        add(
            wishlist=wishlist_1,
        ),
        add(
            wishlist=wishlist_1,
        ),
        add(
            wishlist=wishlist_1,
        ),
    )

    b.wishlist = wishlist_2
    b.save()

    assert ids_in_order(wishlist_1) == [a.pk, c.pk]
    assert positions(wishlist_1) == [0, 1]
    assert positions(wishlist_2) == [0]


# ---------------------------------------------------------- database constraints


def test_database_rejects_duplicated_positions_written_around_the_model() -> None:
    wishlist = wishlist_of(make_user())
    a, b = add(wishlist), add(wishlist)

    with pytest.raises(IntegrityError), transaction.atomic():
        UserWishlistItemModel.objects.filter(pk=b.pk).update(position=position_of(a))
        connection.check_constraints()


def test_invariants_hold_after_the_operations_are_committed() -> None:
    wishlist = wishlist_of(make_user())
    items = [add(wishlist) for _ in range(4)]

    items[0].position = 3
    items[0].save()
    connection.check_constraints()

    assert positions(wishlist) == [0, 1, 2, 3]
    assert UserWishlistItemModel.objects.filter(wishlist=wishlist).count() == 4


def test_deleting_a_wishlist_cascades_its_items_without_errors() -> None:
    user = make_user()
    wishlist = wishlist_of(user)
    add(wishlist)
    add(wishlist)

    user.delete()

    assert UserWishlistItemModel.objects.count() == 0
