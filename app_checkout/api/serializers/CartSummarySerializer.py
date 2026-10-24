from rest_framework import serializers

from app_checkout.models.CartItemManagerModel import CartSummary

from .CartItemSerializer import CartItemSerializer


class CartSummarySerializer(serializers.Serializer[CartSummary]):
    items = CartItemSerializer(
        many=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    discount_total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
