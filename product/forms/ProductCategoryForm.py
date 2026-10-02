from typing import TYPE_CHECKING

from django import forms

from product.models import ProductCategoryModel

from .mixins import NormalizedProductNameFieldMixin

if TYPE_CHECKING:
    BaseProductCategoryForm = forms.ModelForm[ProductCategoryModel]
else:
    BaseProductCategoryForm = forms.ModelForm


class ProductCategoryForm(
    NormalizedProductNameFieldMixin,
    BaseProductCategoryForm,
):
    class Meta:
        model = ProductCategoryModel
        fields = (
            "active",
            "name",
        )
