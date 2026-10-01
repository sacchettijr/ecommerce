from django.db import models
from django.utils.text import slugify


def generate_slug(
    value: str,
) -> str:
    slug: str = slugify(value)

    if not slug:
        raise ValueError(f"It was not possible to create a valid slug for {value!r}.")

    return slug


def generate_unique_slug(
    instance: models.Model,
    value: str,
    slug_field: str = "slug",
) -> str:
    model = type(instance)

    field = model._meta.get_field(
        field_name=slug_field,
    )

    if not isinstance(field, models.Field):
        raise TypeError(f"The field {slug_field!r} is not a concrete model field.")

    max_length: int | None = field.max_length

    base_slug: str = generate_slug(value)

    if max_length:
        base_slug = base_slug[:max_length].rstrip("-")

    queryset = model._default_manager.filter(
        **{
            f"{slug_field}__startswith": base_slug,
        }
    ).exclude(
        pk=instance.pk,
    )

    slug: str = base_slug
    counter = 1

    while queryset.filter(
        **{
            slug_field: slug,
        },
    ).exists():
        suffix: str = f"-{counter}"

        if max_length:
            available_length = max_length - len(suffix)

            if available_length <= 0:
                raise ValueError(
                    f"The field {slug_field!r} does not have enough space to "
                    "generate a unique slug."
                )
            slug = f"{base_slug[:available_length].rstrip('-')}{suffix}"
        else:
            slug = f"{base_slug}{suffix}"

        counter += 1

    return slug
