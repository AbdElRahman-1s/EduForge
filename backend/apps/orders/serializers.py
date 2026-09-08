from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Resource shape for an order (reserved for the order-history issue)."""

    class Meta:
        model = Order
        fields = [
            "id",
            "course_id",
            "amount",
            "status",
            "provider_reference",
            "created_at",
        ]
        read_only_fields = fields
