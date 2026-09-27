from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from diagnostics.models import (
    CentreTest,
    DiagnosticCentre,
    DiagnosticTest,
)


class BookingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bookinguser",
            password="TestPassword123",
        )

        self.centre = DiagnosticCentre.objects.create(
            name="Test Diagnostics",
            location="Chandigarh",
        )

        self.test = DiagnosticTest.objects.create(
            name="Blood Test",
        )

        self.centre_test = CentreTest.objects.create(
            centre=self.centre,
            test=self.test,
            price="500.00",
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_create_booking(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre_test": self.centre_test.id,
                "appointment_datetime": "2026-10-05T10:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["amount"],
            "500.00",
        )

        self.assertEqual(
            response.data["status"],
            "PENDING",
        )

    def test_user_only_sees_own_bookings(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="TestPassword123",
        )

        self.client.post(
            "/api/bookings/",
            {
                "centre_test": self.centre_test.id,
                "appointment_datetime": "2026-10-05T10:00:00Z",
            },
            format="json",
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.get("/api/bookings/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data,
            [],
        )