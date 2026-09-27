from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class SignupTests(APITestCase):
    def test_user_can_signup(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="TestPassword123",
        )

    def test_user_can_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "loginuser",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
