from typing import cast

import pytest
from django.db import IntegrityError, transaction

from app_account.models import UserModel, UserWishlistItemModel, UserWishlistModel
from app_account.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def make_user(**kwargs: object) -> UserModel:
    return cast(UserModel, UserFactory(**kwargs))


def wishlist_of(user: UserModel) -> UserWishlistModel:
    return UserWishlistModel.objects.get(user=user)


# ---------------------------------------------------------- auto-creation (signup/creation flows)


def test_creating_a_user_automatically_creates_their_wishlist() -> None:
    user = make_user()

    assert UserWishlistModel.objects.filter(user=user).count() == 1


def test_wishlist_created_automatically_starts_empty() -> None:
    user = make_user()

    assert UserWishlistItemModel.objects.filter(wishlist=wishlist_of(user)).count() == 0


def test_creating_a_superuser_also_creates_a_wishlist() -> None:
    user = UserModel.objects.create_superuser(
        email="admin-wishlist-test@example.com",
        password="admin123",
        name="Admin",
        date_birth="2000-01-01",
    )

    assert UserWishlistModel.objects.filter(user=user).count() == 1


def test_updating_a_user_does_not_create_a_second_wishlist() -> None:
    user = make_user()

    user.name = "Updated Name"
    user.save()

    assert UserWishlistModel.objects.filter(user=user).count() == 1


def test_saving_a_user_multiple_times_stays_idempotent() -> None:
    user = make_user()

    for _ in range(3):
        user.save()

    assert UserWishlistModel.objects.filter(user=user).count() == 1


def test_re_running_the_signal_manually_is_idempotent() -> None:
    #   Mirrors what a management command or a data migration re-running the creation
    #   logic would see: get_or_create must not raise nor duplicate.
    user = make_user()

    UserWishlistModel.objects.get_or_create(user=user)
    UserWishlistModel.objects.get_or_create(user=user)

    assert UserWishlistModel.objects.filter(user=user).count() == 1


# ---------------------------------------------------------- one wishlist per user


def test_a_user_cannot_have_a_second_wishlist() -> None:
    user = make_user()

    with pytest.raises(IntegrityError), transaction.atomic():
        UserWishlistModel.objects.create(user=user)


def test_wishlist_is_independent_per_user() -> None:
    user_1, user_2 = make_user(), make_user()

    assert wishlist_of(user_1).pk != wishlist_of(user_2).pk


# ---------------------------------------------------------- deletion


def test_deleting_a_user_deletes_their_wishlist() -> None:
    user = make_user()
    wishlist_pk = wishlist_of(user).pk

    user.delete()

    assert UserWishlistModel.objects.filter(pk=wishlist_pk).count() == 0
