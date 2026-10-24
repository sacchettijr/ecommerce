from typing import (
    Any,
    cast,
)

from django.contrib import messages
from django.utils.translation import (
    gettext_lazy as _,
)
from django.views.generic import RedirectView
from rest_framework.generics import get_object_or_404

from app_account.models import UserModel
from app_checkout.models import CartItemModel
from app_product.models import ProductModel


class CartItemCreateView(RedirectView):
    def get_redirect_url(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str | None:

        product = get_object_or_404(
            queryset=ProductModel,
            slug=self.kwargs["slug"],
        )
        if self.request.user.is_authenticated:
            user = cast(
                UserModel,
                self.request.user,
            )
            CartItemModel.objects.add_item(
                user=user,
                product=product,
            )

            messages.success(
                self.request,
                message=_(
                    message="Product added successfully.",
                ),
            )

        return product.get_absolute_url()
