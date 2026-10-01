import os


def env(
    name: str,
    default: str | None = None,
) -> str:
    value: str | None = os.getenv(name)

    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f"Environment variable '{name}' not defined.")

    return value


def env_bool(
    name: str,
    default: bool = False,
) -> bool:
    value: str = (
        env(
            name,
            default=str(default),
        )
        .strip()
        .lower()
    )

    if value in {
        "true",
        "1",
        "yes",
        "y",
        "on",
    }:
        return True

    if value in {
        "false",
        "0",
        "no",
        "n",
        "off",
    }:
        return False

    raise ValueError(
        f"Invalid value for environment variable '{name}': {value!r}. Use true or false."
    )


def env_int(
    name: str,
    default: int | None = None,
) -> int:
    value: str = env(
        name,
        default=(str(default) if default is not None else None),
    )

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid value for environment variable '{name}': {value!r}. An integer was expected."
        ) from exc


def env_list(
    name: str,
    default: list[str] | None = None,
    separator: str = ",",
) -> list[str]:
    default_value: str | None = separator.join(default) if default is not None else None

    value: str = env(
        name,
        default=default_value,
    )

    return [item.strip() for item in value.split(sep=separator) if item.strip()]
