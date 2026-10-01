from django.db.models.fields.files import ImageFieldFile
from django.utils.html import format_html


def image_preview(
    image: ImageFieldFile,
) -> str:
    if not image:
        return "-"
    return format_html(
        format_string=(
            '<img src="{url}" alt="" style="height: 60px; width: 60px; object-fit: cover;">'
        ),
        url=image.url,
    )
