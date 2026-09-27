import uuid
from django.db import transaction
from rest_framework import generics, serializers,status
from rest_framework.permissions import IsAuthenticated

from bookings.models import Booking

from .models import Payment
from .serializers import PaymentSerializer,PaymentWebhookSerializer,PaymentCreateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]
        simulate_success = serializer.validated_data["simulate_success"]

        if booking.user != request.user:
            raise serializers.ValidationError(
                {"booking": "You can only pay for your own booking."}
            )

        if booking.status != Booking.Status.PENDING:
            raise serializers.ValidationError(
                {"booking": "Payment is only allowed for pending bookings."}
            )

        if simulate_success:
            payment_status = Payment.Status.SUCCESS
            booking_status = Booking.Status.CONFIRMED
        else:
            payment_status = Payment.Status.FAILED
            booking_status = Booking.Status.FAILED

        with transaction.atomic():
            booking.status = booking_status
            booking.save(update_fields=["status", "updated_at"])

            payment = Payment.objects.create(
                booking=booking,
                event_id=str(uuid.uuid4()),
                amount=booking.amount,
                status=payment_status,
                provider_reference=f"MOCK-{uuid.uuid4().hex[:12].upper()}",
            )

        response_serializer = PaymentSerializer(payment)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class PaymentWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event_id"]
        booking = serializer.validated_data["booking"]
        payment_status = serializer.validated_data["status"]

        existing_payment = Payment.objects.filter(
            event_id=event_id
        ).first()

        if existing_payment:
            return Response(
                PaymentSerializer(existing_payment).data,
                status=status.HTTP_200_OK,
            )

        if booking.user != request.user:
            raise serializers.ValidationError(
                {"booking": "You can only process your own booking."}
            )

        if payment_status == Payment.Status.SUCCESS:
            booking_status = Booking.Status.CONFIRMED
        else:
            booking_status = Booking.Status.FAILED

        with transaction.atomic():
            payment = Payment.objects.create(
                booking=booking,
                event_id=event_id,
                amount=booking.amount,
                status=payment_status,
                provider_reference=f"MOCK-WEBHOOK-{event_id}",
            )

            booking.status = booking_status
            booking.save(update_fields=["status", "updated_at"])

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
