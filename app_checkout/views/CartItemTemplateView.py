from typing import Any

from django.forms import modelformset_factory
from django.views.generic import TemplateView

from app_checkout.models import CartItemModel


class CartItemTemplateView(TemplateView):
    template_name = "checkout/cart.html"

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        CartItemFormSet = modelformset_factory(
            model=CartItemModel,
            fields=("quantity",),
            can_delete=True,
            extra=0,
        )

        if self.request.user.is_authenticated:
            context["formset"] = CartItemFormSet(
                queryset=CartItemModel.objects.filter(
                    user=self.request.user,
                )
            )
        else:
            context["formset"] = CartItemFormSet(
                queryset=CartItemModel.objects.none(),
            )

        return context
