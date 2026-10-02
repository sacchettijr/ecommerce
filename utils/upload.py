import uuid
from pathlib import Path


def generate_upload_path(
    filename: str,
    directory: str,
    identifier: int | str,
) -> str:
    extension: str = Path(filename).suffix.lower()
    token: str = uuid.uuid4().hex[:12]

    return f"{directory}/{identifier}/{token}{extension}"
