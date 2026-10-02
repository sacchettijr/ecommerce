import io
from typing import (
    Any,
    cast,
)

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import (
    IntegrityError,
    connection,
    transaction,
)
from django.forms import inlineformset_factory
from django.test import Client
from PIL import Image

from product.forms import ProductImageForm
from product.models import (
    ProductImageModel,
    ProductModel,
)
from product.tests.factories import (
    ProductFactory,
    ProductImageFactory,
)

pytestmark = pytest.mark.django_db


def make_product() -> ProductModel:
    return cast(ProductModel, ProductFactory())


def add(product: ProductModel, order: int, *, primary: bool = False) -> ProductImageModel:
    return cast(
        ProductImageModel,
        ProductImageFactory(
            product=product,
            order=order,
            is_primary=primary,
            image__width=40,
            image__height=40,
        ),
    )


def orders(product: ProductModel) -> list[int]:
    return list(
        ProductImageModel.objects.filter(product=product).values_list("order", flat=True),
    )


def ids_in_order(product: ProductModel) -> list[int]:
    return list(
        ProductImageModel.objects.filter(product=product).values_list("pk", flat=True),
    )


def primaries(product: ProductModel) -> list[int]:
    return list(
        ProductImageModel.objects.filter(product=product, is_primary=True).values_list(
            "pk",
            flat=True,
        ),
    )


def is_primary(image: ProductImageModel) -> bool:
    return cast(bool, ProductImageModel.objects.get(pk=image.pk).is_primary)


def order_of(image: ProductImageModel) -> int:
    return cast(int, ProductImageModel.objects.get(pk=image.pk).order)


def reload(image: ProductImageModel) -> ProductImageModel:
    return ProductImageModel.objects.get(pk=image.pk)


# ---------------------------------------------------------- is_primary


def test_product_without_primary_stays_without_primary() -> None:
    product = make_product()
    add(product, 0)
    add(product, 1)

    assert primaries(product) == []


def test_single_primary() -> None:
    product = make_product()
    first = add(product, 0, primary=True)
    add(product, 1)

    assert primaries(product) == [first.pk]


def test_marking_another_image_as_primary_unmarks_the_previous_one() -> None:
    product = make_product()
    first = add(product, 0, primary=True)
    second = add(product, 1)
    third = add(product, 2)

    third.is_primary = True
    third.save()

    assert primaries(product) == [third.pk]
    assert is_primary(first) is False
    assert is_primary(second) is False


def test_creating_a_new_primary_unmarks_the_previous_one() -> None:
    product = make_product()
    first = add(product, 0, primary=True)
    second = add(product, 1, primary=True)

    assert primaries(product) == [second.pk]
    assert is_primary(first) is False


def test_primary_of_other_products_is_untouched() -> None:
    product_1, product_2 = make_product(), make_product()
    image_1 = add(product_1, 0, primary=True)
    image_2 = add(product_2, 0, primary=True)

    other = add(product_1, 1, primary=True)

    assert primaries(product_1) == [other.pk]
    assert primaries(product_2) == [image_2.pk]
    assert is_primary(image_1) is False


# ---------------------------------------------------------- order


def test_sequential_orders_are_kept() -> None:
    product = make_product()
    for order in (0, 1, 2):
        add(product, order)

    assert orders(product) == [0, 1, 2]


def test_two_images_with_order_zero() -> None:
    product = make_product()
    first = add(product, 0)
    second = add(product, 0)

    assert orders(product) == [0, 1]
    assert order_of(second) == 0
    assert order_of(first) == 1


def test_insert_with_used_order_shifts_the_following_images() -> None:
    product = make_product()
    a, b, c = (add(product, order) for order in (0, 1, 2))

    d = add(product, 1)

    assert ids_in_order(product) == [a.pk, d.pk, b.pk, c.pk]
    assert orders(product) == [0, 1, 2, 3]


def test_insert_in_the_middle_of_a_longer_sequence() -> None:
    product = make_product()
    images = [add(product, order) for order in range(5)]

    new = add(product, 2)

    expected = [images[0].pk, images[1].pk, new.pk, images[2].pk, images[3].pk, images[4].pk]
    assert ids_in_order(product) == expected
    assert orders(product) == [0, 1, 2, 3, 4, 5]


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ([0, 1, 4], [0, 1, 2]),
        ([0, 2, 5], [0, 1, 2]),
        ([10, 30, 50, 77], [0, 1, 2, 3]),
    ],
)
def test_gaps_and_arbitrary_orders_are_normalized(given: list[int], expected: list[int]) -> None:
    product = make_product()
    created = [add(product, order) for order in given]

    assert orders(product) == expected
    assert ids_in_order(product) == [image.pk for image in created]


def test_existing_gaps_are_closed_on_the_next_save() -> None:
    product = make_product()
    a, b = add(product, 0), add(product, 1)
    c = add(product, 2)
    ProductImageModel.objects.filter(pk=c.pk).update(order=9)

    a.save()

    assert orders(product) == [0, 1, 2]
    assert ids_in_order(product) == [a.pk, b.pk, c.pk]


def test_orders_are_independent_per_product() -> None:
    product_1, product_2 = make_product(), make_product()
    for order in (0, 1, 2):
        add(product_1, order)
    add(product_2, 0)
    add(product_2, 1)
    before = dict(ProductImageModel.objects.filter(product=product_2).values_list("pk", "order"))

    add(product_1, 0)

    assert orders(product_1) == [0, 1, 2, 3]
    assert (
        dict(ProductImageModel.objects.filter(product=product_2).values_list("pk", "order"))
        == before
    )


# ---------------------------------------------------------- update


def test_changing_the_order_of_an_existing_image() -> None:
    product = make_product()
    a, b, c = (add(product, order) for order in (0, 1, 2))

    c.order = 0
    c.save()

    assert ids_in_order(product) == [c.pk, a.pk, b.pk]
    assert orders(product) == [0, 1, 2]


def test_moving_an_image_to_the_end() -> None:
    product = make_product()
    a, b, c = (add(product, order) for order in (0, 1, 2))

    a.order = 99
    a.save()

    assert ids_in_order(product) == [b.pk, c.pk, a.pk]
    assert orders(product) == [0, 1, 2]


def test_changing_order_and_primary_together() -> None:
    product = make_product()
    a = add(product, 0, primary=True)
    b = add(product, 1)
    c = add(product, 2)

    c.order = 0
    c.is_primary = True
    c.save()

    assert ids_in_order(product) == [c.pk, a.pk, b.pk]
    assert orders(product) == [0, 1, 2]
    assert primaries(product) == [c.pk]


def test_moving_an_image_to_another_product_closes_the_gap_in_the_origin() -> None:
    product_1, product_2 = make_product(), make_product()
    a, b, c = (add(product_1, order) for order in (0, 1, 2))
    add(product_2, 0)

    b.product = product_2
    b.save()

    assert ids_in_order(product_1) == [a.pk, c.pk]
    assert orders(product_1) == [0, 1]
    assert orders(product_2) == [0, 1]


# ---------------------------------------------------------- delete


def test_deleting_the_middle_image_closes_the_gap() -> None:
    product = make_product()
    a, b, c = (add(product, order) for order in (0, 1, 2))

    b.delete()

    assert ids_in_order(product) == [a.pk, c.pk]
    assert orders(product) == [0, 1]


def test_queryset_delete_also_normalizes() -> None:
    product = make_product()
    a, b, c = (add(product, order) for order in (0, 1, 2))

    ProductImageModel.objects.filter(pk=a.pk).delete()

    assert ids_in_order(product) == [b.pk, c.pk]
    assert orders(product) == [0, 1]


def test_deleting_the_primary_promotes_the_first_remaining_image() -> None:
    product = make_product()
    a = add(product, 0, primary=True)
    b, c = add(product, 1), add(product, 2)

    a.delete()

    assert primaries(product) == [b.pk]
    assert is_primary(c) is False


def test_deleting_a_non_primary_keeps_the_primary() -> None:
    product = make_product()
    a = add(product, 0, primary=True)
    b = add(product, 1)

    b.delete()

    assert primaries(product) == [a.pk]


def test_deleting_the_only_image_leaves_the_product_without_images() -> None:
    product = make_product()
    only = add(product, 0, primary=True)

    only.delete()

    assert ProductImageModel.objects.filter(product=product).count() == 0


def test_deleting_a_product_cascades_without_errors() -> None:
    product = make_product()
    add(product, 0, primary=True)
    add(product, 1)

    product.delete()

    assert ProductImageModel.objects.count() == 0


# ---------------------------------------------------------- database constraints


def test_database_rejects_duplicated_orders_written_around_the_model() -> None:
    product = make_product()
    a, b = add(product, 0), add(product, 1)

    with pytest.raises(IntegrityError), transaction.atomic():
        ProductImageModel.objects.filter(pk=b.pk).update(order=order_of(a))
        connection.check_constraints()


def test_database_rejects_two_primaries_written_around_the_model() -> None:
    product = make_product()
    add(product, 0, primary=True)
    b = add(product, 1)

    with pytest.raises(IntegrityError), transaction.atomic():
        ProductImageModel.objects.filter(pk=b.pk).update(is_primary=True)


def test_invariants_hold_after_the_operations_are_committed() -> None:
    product = make_product()
    for order in (5, 5, 0, 9):
        add(product, order, primary=True)

    connection.check_constraints()

    assert orders(product) == [0, 1, 2, 3]
    assert len(primaries(product)) == 1


# ---------------------------------------------------------- admin (inline formset)


def formset_data(rows: list[dict[str, Any]], initial: int) -> dict[str, Any]:
    prefix = "images"
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


def png(name: str) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (30, 30), "red").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def image_formset_class(extra: int) -> Any:
    return inlineformset_factory(
        ProductModel,
        ProductImageModel,
        form=ProductImageForm,
        fields=("image", "is_primary", "order"),
        extra=extra,
    )


def test_inline_formset_saving_several_images_at_once() -> None:
    product = make_product()
    data = formset_data(
        [
            {"order": "0", "is_primary": "on"},
            {"order": "0", "is_primary": "on"},
            {"order": "7"},
        ],
        initial=0,
    )
    files = {f"images-{index}-image": png(f"{index}.png") for index in range(3)}
    formset = image_formset_class(extra=3)(data, files, instance=product, prefix="images")

    assert formset.is_valid(), formset.errors
    with transaction.atomic():
        formset.save()

    connection.check_constraints()
    assert orders(product) == [0, 1, 2]
    assert len(primaries(product)) == 1


def test_inline_formset_swapping_the_order_of_two_existing_images() -> None:
    product = make_product()
    a, b = add(product, 0), add(product, 1)
    data = formset_data(
        [
            {"id": a.pk, "product": product.pk, "order": "1"},
            {"id": b.pk, "product": product.pk, "order": "0"},
        ],
        initial=2,
    )
    formset = image_formset_class(extra=0)(data, {}, instance=product, prefix="images")

    assert formset.is_valid(), formset.errors
    with transaction.atomic():
        formset.save()

    connection.check_constraints()
    assert ids_in_order(product) == [b.pk, a.pk]
    assert orders(product) == [0, 1]


# ---------------------------------------------------------- API (read-only)


def test_public_api_lists_images_in_the_normalized_order(client: Client) -> None:
    product = make_product()
    first = add(product, 0)
    second = add(product, 0)

    response = client.get(f"/api/product/products/{cast(str, product.slug)}/")

    assert response.status_code == 200
    assert [image["id"] for image in response.json()["images"]] == [second.pk, first.pk]
