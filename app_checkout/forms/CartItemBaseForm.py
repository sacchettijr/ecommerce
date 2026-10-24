from typing import TYPE_CHECKING

from django import forms

from app_checkout.models import CartItemModel

if TYPE_CHECKING:
    BaseCartItemModelForm = forms.ModelForm[CartItemModel]
else:
    BaseCartItemModelForm = forms.ModelForm


class CartItemBaseForm(BaseCartItemModelForm):
    pass
