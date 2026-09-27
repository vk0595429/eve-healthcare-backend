from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        centre_test = serializer.validated_data["centre_test"]

        serializer.save(
            user=self.request.user,
            amount=centre_test.price,
            status=Booking.Status.PENDING,
        )