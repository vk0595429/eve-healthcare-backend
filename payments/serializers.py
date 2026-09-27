from rest_framework import serializers
from bookings.models import Booking
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "event_id",
            "amount",
            "status",
            "provider_reference",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "event_id",
            "amount",
            "status",
            "provider_reference",
            "created_at",
        ]

class PaymentWebhookSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=100)
    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all()
    )
    status = serializers.ChoiceField(
        choices=Payment.Status.choices
    )


class PaymentCreateSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all()
    )
    simulate_success = serializers.BooleanField(default=True)