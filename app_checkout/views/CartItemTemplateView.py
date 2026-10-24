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

        session_key = self.request.session.session_key

        if session_key:
            context["formset"] = CartItemFormSet(
                queryset=CartItemModel.objects.filter(
                    cart_key=session_key,
                )
            )
        else:
            context["formset"] = CartItemFormSet(
                queryset=CartItemModel.objects.none(),
            )

        return context
