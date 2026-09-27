from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from diagnostics.models import (
    CentreTest,
    DiagnosticCentre,
    DiagnosticTest,
)


class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="paymentuser",
            password="TestPassword123",
        )

        self.other_user = User.objects.create_user(
            username="otherpaymentuser",
            password="TestPassword123",
        )

        self.centre = DiagnosticCentre.objects.create(
            name="Payment Diagnostics",
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

        self.booking = Booking.objects.create(
            user=self.user,
            centre_test=self.centre_test,
            appointment_datetime="2026-10-10T10:00:00Z",
            amount="500.00",
            status=Booking.Status.PENDING,
        )

        self.client.force_authenticate(user=self.user)

    def test_successful_payment_confirms_booking(self):
        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
                "simulate_success": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

        self.assertEqual(
            response.data["status"],
            "SUCCESS",
        )

    def test_failed_payment_marks_booking_failed(self):
        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
                "simulate_success": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.FAILED,
        )

        self.assertEqual(
            response.data["status"],
            "FAILED",
        )

    def test_user_cannot_pay_for_another_users_booking(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
                "simulate_success": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["booking"],
            "You can only pay for your own booking.",
        )

    def test_payment_not_allowed_for_processed_booking(self):
        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()

        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
                "simulate_success": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_webhook_is_idempotent(self):
        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "webhook-test-001",
                "booking": self.booking.id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

        first_payment_id = response.data["id"]

        # Send the exact same webhook event again
        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "webhook-test-001",
                "booking": self.booking.id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            first_payment_id,
        )

        self.assertEqual(
            self.booking.payments.count(),
            1,
        )

    def test_user_cannot_process_another_users_webhook(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "unauthorized-webhook-001",
                "booking": self.booking.id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["booking"],
            "You can only process your own booking.",
        )