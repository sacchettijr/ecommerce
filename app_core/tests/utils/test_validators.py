from decimal import Decimal
from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from utils.validator import (
    validate_alpha,
    validate_image_dimensions,
    validate_image_extension,
    validate_image_max_size,
    validate_max_length,
    validate_min_length,
    validate_name,
    validate_non_negative_decimal,
    validate_positive_decimal,
)


def test_a_full_name_with_first_and_last_name_is_accepted() -> None:
    validate_name(value="Maria da Silva")


def test_a_single_word_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_name(value="Maria")


def test_an_empty_value_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_name(value="")


def test_whitespace_only_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_name(value="   ")


def test_a_value_with_no_letters_at_all_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate_name(value="123 456")


def test_a_stray_punctuation_only_part_does_not_count_as_a_second_name() -> None:
    #   "Maria -" has two whitespace-separated parts, but the second one has no letters.
    with pytest.raises(ValidationError):
        validate_name(value="Maria -")


def test_leading_and_trailing_whitespace_around_two_names_is_still_accepted() -> None:
    validate_name(value="  Jane Doe  ")


def test_more_than_two_names_is_accepted() -> None:
    validate_name(value="Maria Eduarda da Silva Santos")


# -------------------------------------------------------------------- decimals


def test_validate_positive_decimal_accepts_a_value_above_zero() -> None:
    validate_positive_decimal(Decimal("0.01"))


def test_validate_positive_decimal_rejects_zero() -> None:
    with pytest.raises(ValidationError):
        validate_positive_decimal(Decimal("0"))


def test_validate_positive_decimal_rejects_a_negative_value() -> None:
    with pytest.raises(ValidationError):
        validate_positive_decimal(Decimal("-1"))


def test_validate_non_negative_decimal_accepts_zero() -> None:
    validate_non_negative_decimal(Decimal("0"))


def test_validate_non_negative_decimal_rejects_a_negative_value() -> None:
    with pytest.raises(ValidationError):
        validate_non_negative_decimal(Decimal("-0.01"))


# ------------------------------------------------------------------------ text


def test_validate_min_length_accepts_a_value_at_the_minimum() -> None:
    validate_min_length(value="abc", min_length=3)


def test_validate_min_length_rejects_a_shorter_value() -> None:
    with pytest.raises(ValidationError):
        validate_min_length(value="ab", min_length=3)


def test_validate_max_length_accepts_a_value_at_the_maximum() -> None:
    validate_max_length(value="abc", max_length=3)


def test_validate_max_length_rejects_a_longer_value() -> None:
    with pytest.raises(ValidationError):
        validate_max_length(value="abcd", max_length=3)


def test_validate_alpha_accepts_letters_only() -> None:
    validate_alpha(value="abcXYZ")


def test_validate_alpha_rejects_digits() -> None:
    with pytest.raises(ValidationError):
        validate_alpha(value="abc123")


def test_validate_alpha_rejects_punctuation() -> None:
    with pytest.raises(ValidationError):
        validate_alpha(value="ab-c")


# ----------------------------------------------------------------------- image


def make_image_file(
    width: int = 10,
    height: int = 10,
    name: str = "test.png",
    size_in_bytes: int | None = None,
) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (width, height), color="blue").save(buffer, format="PNG")
    content = buffer.getvalue()
    if size_in_bytes is not None:
        content += b"\0" * max(0, size_in_bytes - len(content))
    return SimpleUploadedFile(name=name, content=content, content_type="image/png")


def test_validate_image_max_size_accepts_a_file_under_the_limit() -> None:
    validate_image_max_size(make_image_file(), max_size=1024 * 1024)


def test_validate_image_max_size_rejects_a_file_over_the_limit() -> None:
    oversized = make_image_file(size_in_bytes=2048)

    with pytest.raises(ValidationError):
        validate_image_max_size(oversized, max_size=1024)


def test_validate_image_dimensions_accepts_a_value_within_every_bound() -> None:
    validate_image_dimensions(
        make_image_file(width=100, height=100),
        min_width=50,
        min_height=50,
        max_width=200,
        max_height=200,
    )


def test_validate_image_dimensions_rejects_an_image_narrower_than_the_minimum() -> None:
    with pytest.raises(ValidationError):
        validate_image_dimensions(make_image_file(width=10, height=100), min_width=50)


def test_validate_image_dimensions_rejects_an_image_shorter_than_the_minimum() -> None:
    with pytest.raises(ValidationError):
        validate_image_dimensions(make_image_file(width=100, height=10), min_height=50)


def test_validate_image_dimensions_rejects_an_image_wider_than_the_maximum() -> None:
    with pytest.raises(ValidationError):
        validate_image_dimensions(make_image_file(width=300, height=100), max_width=200)


def test_validate_image_dimensions_rejects_an_image_taller_than_the_maximum() -> None:
    with pytest.raises(ValidationError):
        validate_image_dimensions(make_image_file(width=100, height=300), max_height=200)


def test_validate_image_extension_accepts_an_allowed_extension() -> None:
    validate_image_extension(make_image_file(name="photo.png"), allowed_extensions={".png", ".jpg"})


def test_validate_image_extension_rejects_a_disallowed_extension() -> None:
    with pytest.raises(ValidationError):
        validate_image_extension(
            make_image_file(name="photo.gif"), allowed_extensions={".png", ".jpg"}
        )


def test_validate_image_extension_is_case_insensitive() -> None:
    validate_image_extension(make_image_file(name="photo.PNG"), allowed_extensions={".png"})
