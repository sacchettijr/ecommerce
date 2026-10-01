import re
from typing import (
    Any,
)


class NormalizedProductDescriptionFieldMixin:
    cleaned_data: dict[str, Any]

    def clean_description(self) -> str:
        description = self.cleaned_data.get("description") or ""

        #   O campo é Markdown: preserva quebras de linha e blocos, só padroniza o texto.
        description = description.replace("\r\n", "\n").replace("\r", "\n").strip()

        return re.sub(
            pattern=r"\n{3,}",
            repl="\n\n",
            string=description,
        )
