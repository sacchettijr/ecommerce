from typing import (
    Any,
)

from utils.validator import (
    validate_image_dimensions,
    validate_image_extension,
    validate_image_max_size,
)


class NormalizedProductThumbnailFieldMixin:
    cleaned_data: dict[str, Any]
    MAX_THUMBNAIL_SIZE_BYTES = 5 * 1024 * 1024

    def clean_thumbnail(self) -> Any:
        thumbnail = self.cleaned_data.get("thumbnail")

        if thumbnail is not None:
            validate_image_max_size(
                image=thumbnail,
                max_size=self.MAX_THUMBNAIL_SIZE_BYTES,
            )

            validate_image_extension(
                image=thumbnail,
                allowed_extensions={
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                },
            )

            validate_image_dimensions(
                image=thumbnail,
                min_width=20,
                min_height=20,
            )

        return thumbnail
