import pytest
from django.test import Client

from app_product.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db


def make_products(count: int) -> None:
    for _ in range(count):
        ProductFactory()


def all_ids_in_order(client: Client, ordering: str | None = None) -> list[int]:
    ids: list[int] = []
    page = 1

    while True:
        query = f"?page={page}" + (f"&ordering={ordering}" if ordering else "")
        response = client.get(f"/api/product/products/{query}")
        assert response.status_code == 200
        body = response.json()
        ids.extend(product["id"] for product in body["results"])

        if page >= body["total_pages"]:
            break
        page += 1

    return ids


def test_default_ordering_is_stable_across_separate_requests(
    client: Client,
) -> None:
    make_products(5)

    first = all_ids_in_order(client)
    second = all_ids_in_order(client)

    assert first == second


def test_default_ordering_has_no_duplicates_or_gaps_across_pages(
    client: Client,
) -> None:
    #   More than one page's worth (PAGE_SIZE=25), to prove paginating through
    #   the randomized default never repeats or skips a product.
    make_products(30)

    ids = all_ids_in_order(client)

    assert len(ids) == len(set(ids)) == 30


def test_explicit_ordering_still_overrides_the_randomized_default(
    client: Client,
) -> None:
    make_products(5)

    response = client.get("/api/product/products/?ordering=name")
    assert response.status_code == 200
    names = [product["name"] for product in response.json()["results"]]

    assert names == sorted(names)


def test_randomized_default_does_not_simply_reproduce_recency_order(
    client: Client,
) -> None:
    #   Not a strict guarantee for every possible hash outcome, but with enough
    #   products the chance of the shuffle coincidentally matching -created_at
    #   exactly is astronomically small - a real assertion, not a flaky one.
    make_products(20)

    default_ids = all_ids_in_order(client)
    recency_ids = all_ids_in_order(client, ordering="-created_at")

    assert default_ids != recency_ids
