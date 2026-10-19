import pytest
from django.core.exceptions import ValidationError

from utils.validator import validate_name


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
