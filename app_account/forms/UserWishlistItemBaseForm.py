from typing import TYPE_CHECKING

from django import forms

from app_account.models import UserWishlistItemModel

if TYPE_CHECKING:
    BaseUserWishlistItemForm = forms.ModelForm[UserWishlistItemModel]
else:
    BaseUserWishlistItemForm = forms.ModelForm


class UserWishlistItemBaseForm(BaseUserWishlistItemForm):
    class Meta:
        model = UserWishlistItemModel
        fields = (
            "wishlist",
            "product",
        )
