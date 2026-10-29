from typing import Any, cast

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory

from app_account.middleware.CurrentUserMiddleware import CurrentUserMiddleware
from app_account.models import UserModel, UserWishlistItemModel
from app_account.tests.factories import UserFactory
from app_product.models import ProductModel
from app_product.tests.factories import ProductFactory
from utils.current_user import get_current_user, set_current_user

pytestmark = pytest.mark.django_db

# ----------------------------------------------------- middleware unit tests


def test_authenticated_request_exposes_the_user_through_get_current_user() -> None:
    user = cast(UserModel, UserFactory())
    seen: list[Any] = []

    def get_response(request: HttpRequest) -> HttpResponse:
        seen.append(get_current_user())
        return HttpResponse()

    middleware = CurrentUserMiddleware(get_response=get_response)
    request = RequestFactory().get("/")
    request.user = user

    middleware(request)

    assert seen == [user]


def test_anonymous_request_exposes_no_current_user() -> None:
    seen: list[Any] = []

    def get_response(request: HttpRequest) -> HttpResponse:
        seen.append(get_current_user())
        return HttpResponse()

    middleware = CurrentUserMiddleware(get_response=get_response)
    request = RequestFactory().get("/")
    request.user = AnonymousUser()

    middleware(request)

    assert seen == [None]


def test_current_user_is_reset_to_none_after_the_response_is_built() -> None:
    user = cast(UserModel, UserFactory())
    middleware = CurrentUserMiddleware(get_response=lambda request: HttpResponse())
    request = RequestFactory().get("/")
    request.user = user

    middleware(request)

    assert get_current_user() is None


def test_current_user_is_reset_even_if_get_response_raises() -> None:
    user = cast(UserModel, UserFactory())
    middleware = CurrentUserMiddleware(
        get_response=lambda request: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    request = RequestFactory().get("/")
    request.user = user

    with pytest.raises(RuntimeError):
        middleware(request)

    assert get_current_user() is None


# ------------------------------------------------- full-stack integration tests


def test_creating_a_row_through_an_authenticated_request_stamps_created_by_and_updated_by(
    client: Client,
) -> None:
    user = cast(UserModel, UserFactory())
    product = cast(ProductModel, ProductFactory())
    client.force_login(user)

    response = client.post("/api/account/wishlist/", data={"product": product.pk})

    assert response.status_code == 201
    item = cast(Any, UserWishlistItemModel.objects.get(wishlist__user=user))
    assert item.created_by_id == user.pk
    assert item.updated_by_id == user.pk


def test_a_row_created_outside_any_request_has_no_created_by_or_updated_by() -> None:
    #   ProductFactory() saves with no current request/user set, so created_by/updated_by
    #   must stay unset — the "no current user" branch of BaseModel.save().
    product = cast(Any, ProductFactory())

    assert product.created_by_id is None
    assert product.updated_by_id is None


def test_created_by_is_set_once_and_preserved_while_updated_by_refreshes_on_every_save() -> None:
    product = cast(ProductModel, ProductFactory())
    creator = cast(UserModel, UserFactory())
    editor = cast(UserModel, UserFactory())

    try:
        set_current_user(user=creator)
        product.name = "First edit"
        product.save()

        set_current_user(user=editor)
        product.name = "Second edit"
        product.save()
    finally:
        set_current_user(user=None)

    product.refresh_from_db()
    refreshed = cast(Any, product)
    assert refreshed.created_by_id == creator.pk
    assert refreshed.updated_by_id == editor.pk


def test_current_user_does_not_leak_between_sequential_requests(client: Client) -> None:
    user = cast(UserModel, UserFactory())
    product = cast(ProductModel, ProductFactory())
    client.force_login(user)
    client.post("/api/account/wishlist/", data={"product": product.pk})

    client.logout()
    other_product = cast(ProductModel, ProductFactory())
    client.post("/api/account/wishlist/", data={"product": other_product.pk})

    #   The anonymous follow-up request must have been rejected (403), not silently
    #   attributed to the previous request's authenticated user.
    assert UserWishlistItemModel.objects.filter(product=other_product).count() == 0
