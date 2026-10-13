from typing import (
    Any,
)

from utils.validator import (
    validate_image_dimensions,
    validate_image_extension,
    validate_image_max_size,
)


class NormalizedProductImageFieldMixin:
    cleaned_data: dict[str, Any]
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

    def clean_image(self) -> Any:
        image = self.cleaned_data.get("image")

        if image is not None:
            validate_image_max_size(
                image=image,
                max_size=self.MAX_IMAGE_SIZE_BYTES,
            )

            validate_image_extension(
                image=image,
                allowed_extensions={
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                },
            )

            validate_image_dimensions(
                image=image,
                min_width=20,
                min_height=20,
            )

        return image
