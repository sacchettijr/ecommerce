from typing import (
    TYPE_CHECKING,
    ClassVar,
)

from django import forms

from app_core.forms.widgets import MarkdownEditorWidget
from app_product.models import (
    ProductModel,
)

from .mixins import (
    NormalizedProductDescriptionFieldMixin,
    NormalizedProductNameFieldMixin,
    NormalizedProductPriceFieldMixin,
    NormalizedProductThumbnailFieldMixin,
)

if TYPE_CHECKING:
    BaseProductForm = forms.ModelForm[ProductModel]
else:
    BaseProductForm = forms.ModelForm


class ProductForm(
    NormalizedProductNameFieldMixin,
    NormalizedProductPriceFieldMixin,
    NormalizedProductDescriptionFieldMixin,
    NormalizedProductThumbnailFieldMixin,
    BaseProductForm,
):
    class Meta:
        model = ProductModel
        fields = (
            "active",
            "category",
            "name",
            "price",
            "thumbnail",
            "description",
        )
        widgets: ClassVar[dict[str, type[forms.Widget]]] = {
            "description": MarkdownEditorWidget,
        }
