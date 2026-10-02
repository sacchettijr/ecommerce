from typing import TYPE_CHECKING

from django import forms

from product.models import ProductImageModel

from .mixins import NormalizedProductImageFieldMixin

if TYPE_CHECKING:
    ModelFormBase = forms.ModelForm[ProductImageModel]
else:
    ModelFormBase = forms.ModelForm


class ProductImageForm(
    NormalizedProductImageFieldMixin,
    ModelFormBase,
):
    class Meta:
        model = ProductImageModel
        fields = (
            "product",
            "image",
            "is_primary",
            "order",
        )
