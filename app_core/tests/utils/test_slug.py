from typing import Any, cast

import pytest

from app_product.models import ProductCategoryModel
from app_product.tests.factories import ProductCategoryFactory
from utils.slug import generate_slug, generate_unique_slug

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------- generate_slug


def test_generate_slug_slugifies_the_value() -> None:
    assert generate_slug("Hello World") == "hello-world"


def test_generate_slug_raises_when_the_value_has_no_slugifiable_characters() -> None:
    with pytest.raises(ValueError, match="not possible to create a valid slug"):
        generate_slug("!!!")


# --------------------------------------------------------- generate_unique_slug


def test_generate_unique_slug_returns_the_base_slug_when_nothing_else_uses_it() -> None:
    category = ProductCategoryModel(name="Furniture")

    slug = generate_unique_slug(instance=category, value="Furniture")

    assert slug == "furniture"


def test_generate_unique_slug_appends_a_counter_suffix_on_collision() -> None:
    ProductCategoryFactory(name="Shoes")

    category = ProductCategoryModel(name="Shoes")
    slug = generate_unique_slug(instance=category, value="Shoes")

    assert slug == "shoes-1"


def test_generate_unique_slug_increments_the_counter_past_existing_suffixes() -> None:
    ProductCategoryFactory(name="Shoes")
    ProductCategoryFactory(name="Shoes")  # becomes "shoes-1" via ProductBaseModel.save()

    category = ProductCategoryModel(name="Shoes")
    slug = generate_unique_slug(instance=category, value="Shoes")

    assert slug == "shoes-2"


def test_generate_unique_slug_excludes_the_instance_itself_so_updates_keep_their_own_slug() -> None:
    category = cast(Any, ProductCategoryFactory(name="Shoes"))

    #   Re-deriving the slug for the very same (already-saved) instance, from its own
    #   current name, must not collide with itself and get a spurious "-1" suffix.
    slug = generate_unique_slug(instance=category, value="Shoes")

    assert slug == category.slug == "shoes"


def test_generate_unique_slug_works_across_different_categories() -> None:
    ProductCategoryFactory(name="Shoes")

    category = ProductCategoryModel(name="Hats")
    slug = generate_unique_slug(instance=category, value="Hats")

    assert slug == "hats"
