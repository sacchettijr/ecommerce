from typing import Any

from django.contrib import messages
from django.utils.translation import (
    gettext_lazy as _,
)
from django.views.generic import RedirectView
from rest_framework.generics import get_object_or_404

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

        if self.request.session.session_key is None:
            self.request.session.save()

        cart_item, created = CartItemModel.objects.add_item(
            cart_key=self.request.session.session_key,
            product=product,
        )

        if created:
            messages.success(
                self.request,
                message=_(
                    message="Product added successfully.",
                ),
            )
        else:
            messages.success(
                self.request,
                message=_(
                    message="Product updated successfully.",
                ),
            )

        return product.get_absolute_url()
