from typing import (
    Any,
    ClassVar,
)

from django import forms

CKEDITOR_VERSION = "48.5.2"
CKEDITOR_PATH = f"lib/ckeditor5-{CKEDITOR_VERSION}"


class MarkdownEditorWidget(forms.Textarea):
    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            attrs={
                "class": "markdown-editor",
                **(attrs or {}),
            },
        )

    class Media:
        css: ClassVar[dict[str, tuple[str, ...]]] = {
            "all": (
                f"{CKEDITOR_PATH}/ckeditor5.css",
                "src/css/admin/markdown_editor.css",
            ),
        }
        js = (
            f"{CKEDITOR_PATH}/ckeditor5.umd.js",
            f"{CKEDITOR_PATH}/translations/pt-br.umd.js",
            f"{CKEDITOR_PATH}/translations/es.umd.js",
            "src/js/admin/markdown_editor.js",
        )
