from typing import TYPE_CHECKING

from django import forms

from app_account.models import UserWishlistModel

if TYPE_CHECKING:
    BaseUserWishlistForm = forms.ModelForm[UserWishlistModel]
else:
    BaseUserWishlistForm = forms.ModelForm


class UserWishlistBaseForm(BaseUserWishlistForm):
    class Meta:
        model = UserWishlistModel
        fields = ("user",)
