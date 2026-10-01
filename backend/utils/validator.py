from decimal import Decimal
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

ZERO: Decimal = Decimal(value="0")


# =========================================================
#   DECIMAL
# =========================================================


def validate_positive_decimal(
    value: Decimal,
) -> None:
    if value <= ZERO:
        raise ValidationError(
            message=_(
                message="The value must be greater than zero.",
            ),
        )


def validate_non_negative_decimal(
    value: Decimal,
) -> None:
    if value < ZERO:
        raise ValidationError(
            message=_(
                message="The value cannot be negative.",
            ),
        )


# =========================================================
#   TEXT
# =========================================================


def validate_min_length(
    value: str,
    min_length: int,
) -> None:
    if len(value) < min_length:
        raise ValidationError(
            message=_(
                message="This field must contain at least %(min_length)d characters.",
            ),
            params={
                "min_length": min_length,
            },
        )


def validate_max_length(
    value: str,
    max_length: int,
) -> None:
    if len(value) > max_length:
        raise ValidationError(
            message=_(
                message="This field must contain at most %(max_length)d characters.",
            ),
            params={
                "max_length": max_length,
            },
        )


def validate_name(
    value: str,
) -> None:

    if not value.strip():
        raise ValidationError(
            message=_(
                message="The name cannot be empty.",
            ),
        )

    if not any(character.isalpha() for character in value):
        raise ValidationError(
            message=_(
                message="The name must contain at least one letter.",
            ),
        )


def validate_alpha(
    value: str,
) -> None:
    if not value.isalpha():
        raise ValidationError(
            message=_(
                message="This field must contain only letters.",
            ),
        )


# =========================================================
#   IMAGE
# =========================================================


def validate_image_max_size(
    image: UploadedFile[Any],
    max_size: int,
) -> None:
    size: int | None = image.size

    if size is None:
        raise ValidationError(
            message=_(
                message="The image must have a size.",
            ),
        )

    if size > max_size:
        raise ValidationError(
            message=_(
                message="The image cannot exceed %(max_size)s MB.",
            ),
            params={
                "max_size": max_size // (1024 * 1024),
            },
        )


def validate_image_dimensions(
    image: UploadedFile[Any],
    min_width: int | None = None,
    min_height: int | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
) -> None:
    width, height = get_image_dimensions(
        file_or_path=image,
    )

    if width is None or height is None:
        raise ValidationError(
            message=_(
                message="It was not possible to determine the image dimensions.",
            ),
        )

    if min_width is not None and width < min_width:
        raise ValidationError(
            message=_(
                message="The image must be at least %(min_width)d pixels wide.",
            ),
            params={
                "min_width": min_width,
            },
        )

    if min_height is not None and height < min_height:
        raise ValidationError(
            message=_(
                message="The image must be at least %(min_height)d pixels high.",
            ),
            params={
                "min_height": min_height,
            },
        )

    if max_width is not None and width > max_width:
        raise ValidationError(
            message=_(
                message="The image cannot exceed %(max_width)d pixels in width.",
            ),
            params={
                "max_width": max_width,
            },
        )

    if max_height is not None and height > max_height:
        raise ValidationError(
            message=_(
                message="The image cannot exceed %(max_height)d pixels in height.",
            ),
            params={
                "max_height": max_height,
            },
        )


def validate_image_extension(
    image: UploadedFile[Any],
    allowed_extensions: set[str],
) -> None:
    if image.name is None:
        raise ValidationError(
            message=_(
                message="The image must have a filename.",
            ),
        )

    extension: str = Path(image.name).suffix.lower()

    normalized_extensions = {
        extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        for extension in allowed_extensions
    }

    if extension not in normalized_extensions:
        raise ValidationError(
            message=_(
                message="The image format is not supported. Allowed formats: %(extensions)s.",
            ),
            params={
                "extensions": ", ".join(
                    sorted(normalized_extensions),
                ),
            },
        )
