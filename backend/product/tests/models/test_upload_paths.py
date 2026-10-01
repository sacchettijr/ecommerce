import re
from pathlib import Path
from typing import (
    Any,
    cast,
)

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ImageField
from django.db.models.fields.files import FieldFile
from pytest_django.fixtures import Settings

from product.models import (
    ProductImageModel,
    ProductModel,
)
from product.models.product_thumbnail_upload_to import product_thumbnail_upload_to
from product.tests.factories import (
    ProductFactory,
    ProductImageFactory,
)
from utils.upload import generate_upload_path

LONG_NAME = "Yawyore Gaming PC AMD Ryzen 7 5700X GeForce RTX 5060 Desktop Computer " * 4
ORIGINAL_FILENAME = "811hke747wl_ac_sl1500_uZxnz3y.jpg"


def make_product(**kwargs: Any) -> ProductModel:
    return cast(ProductModel, ProductFactory(**kwargs))


def make_image(**kwargs: Any) -> ProductImageModel:
    return cast(ProductImageModel, ProductImageFactory(**kwargs))


def stored_name(field: FieldFile | None) -> str:
    assert field is not None
    assert field.name is not None
    return field.name


def stored_path(field: FieldFile | None) -> str:
    assert field is not None
    return field.path


def slug_of(product: ProductModel) -> str:
    return cast(str, product.slug)


def upload(filename: str = ORIGINAL_FILENAME) -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name=filename,
        content=b"not-a-real-image",
        content_type="image/jpeg",
    )


@pytest.fixture(autouse=True)
def media_root(
    settings: Settings,
    tmp_path: Path,
) -> None:
    settings.MEDIA_ROOT = str(tmp_path)


# =========================================================
#   generate_upload_path
# =========================================================


def test_generate_upload_path_keeps_only_the_lowercase_extension() -> None:
    path = generate_upload_path(
        filename="FOTO.PNG",
        directory="products",
        identifier=7,
    )

    assert re.fullmatch(r"products/7/[0-9a-f]{12}\.png", path)


def test_generate_upload_path_supports_names_without_latin_characters() -> None:
    path = generate_upload_path(
        filename="日本語.png",
        directory="products",
        identifier=7,
    )

    assert re.fullmatch(r"products/7/[0-9a-f]{12}\.png", path)


def test_generate_upload_path_ignores_the_original_name_length() -> None:
    path = generate_upload_path(
        filename=f"{'a' * 300}.jpg",
        directory="products",
        identifier=7,
    )

    assert len(path) < 40


def test_generate_upload_path_is_unique_for_the_same_filename() -> None:
    paths = {
        generate_upload_path(
            filename=ORIGINAL_FILENAME,
            directory="products",
            identifier=7,
        )
        for _ in range(200)
    }

    assert len(paths) == 200


# =========================================================
#   ProductModel.thumbnail
# =========================================================


@pytest.mark.django_db
def test_thumbnail_is_stored_under_the_product_id_on_creation() -> None:
    product = make_product(name=LONG_NAME, thumbnail=upload())

    name = stored_name(product.thumbnail)
    match = re.fullmatch(r"products/thumbnails/(?P<id>\d+)/[0-9a-f]{12}\.jpg", name)

    assert match is not None
    assert int(match["id"]) == product.pk


@pytest.mark.django_db
def test_thumbnail_path_does_not_contain_the_slug() -> None:
    product = make_product(name=LONG_NAME, thumbnail=upload())

    assert len(slug_of(product)) > 100
    assert slug_of(product) not in stored_name(product.thumbnail)


@pytest.mark.django_db
def test_thumbnail_path_fits_the_field_max_length_with_a_very_long_slug() -> None:
    product = make_product(name=LONG_NAME, thumbnail=upload())

    field = ProductModel._meta.get_field("thumbnail")

    assert isinstance(field, ImageField)
    max_length = field.max_length

    assert max_length is not None
    assert len(stored_name(product.thumbnail)) <= max_length
    assert len(stored_name(product.thumbnail)) < 50


@pytest.mark.django_db
def test_thumbnail_file_is_written_to_storage() -> None:
    product = make_product(thumbnail=upload())

    assert Path(stored_path(product.thumbnail)).is_file()


@pytest.mark.django_db
def test_thumbnail_preserves_the_original_extension() -> None:
    product = make_product(thumbnail=upload("FOTO.WEBP"))

    assert stored_name(product.thumbnail).endswith(".webp")


@pytest.mark.django_db
def test_thumbnail_is_optional() -> None:
    product = make_product()

    assert not product.thumbnail


@pytest.mark.django_db
def test_replacing_the_thumbnail_of_an_existing_product_uses_the_same_directory() -> None:
    product = make_product(thumbnail=upload())
    first = stored_name(product.thumbnail)

    product.thumbnail = upload()
    product.save()

    current = stored_name(product.thumbnail)

    assert current is not None
    assert current != first
    assert current.startswith(f"products/thumbnails/{product.pk}/")


@pytest.mark.django_db
def test_thumbnails_with_the_same_filename_do_not_collide() -> None:
    first = make_product(thumbnail=upload())
    second = make_product(thumbnail=upload())

    assert stored_name(first.thumbnail) != stored_name(second.thumbnail)
    assert Path(stored_path(first.thumbnail)).is_file()
    assert Path(stored_path(second.thumbnail)).is_file()


@pytest.mark.django_db
def test_thumbnail_upload_to_requires_a_saved_product() -> None:
    class UnsavedProduct:
        pk = None

    with pytest.raises(ValueError):
        product_thumbnail_upload_to(
            instance=UnsavedProduct(),
            filename=ORIGINAL_FILENAME,
        )


# =========================================================
#   ProductImageModel.image
# =========================================================


@pytest.mark.django_db
def test_gallery_image_is_stored_under_the_product_id() -> None:
    product = make_product(name=LONG_NAME)
    image = make_image(product=product, image=upload("a" * 200 + ".JPEG"))

    assert re.fullmatch(rf"products/{product.pk}/[0-9a-f]{{12}}\.jpeg", stored_name(image.image))
    assert slug_of(product) not in stored_name(image.image)


@pytest.mark.django_db
def test_gallery_images_with_the_same_filename_do_not_collide() -> None:
    product = make_product()
    first = make_image(product=product, image=upload())
    second = make_image(product=product, image=upload())

    assert stored_name(first.image) != stored_name(second.image)
    assert Path(first.image.path).is_file()
    assert Path(second.image.path).is_file()
