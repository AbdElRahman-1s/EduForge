from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("registeration")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.profile_url = reverse("profile")

        self.user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
        }

        self.existing_user = User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="ExistingPassword123!",
        )

    # Registration

    def test_successful_registration(self):
        """Should create a new user and return a 201 status code."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"], self.user_data["username"])
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_registration_password_mismatch(self):
        """Should fail with 400 if passwords do not match."""
        self.user_data["confirm_password"] = "DifferentPassword123!"
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", response.data)

    def test_registration_invalid_username_regex(self):
        """Should fail with 400 if username contains spaces or invalid symbols."""
        self.user_data["username"] = "invalid name!"
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Login

    def test_successful_login(self):
        """Should authenticate valid credentials and return access/refresh tokens."""
        login_payload = {
            "email": "existing@example.com",
            "password": "ExistingPassword123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], login_payload["email"])

    def test_login_invalid_password(self):
        """Should reject right email with wrong password with 401."""
        login_payload = {
            "email": "existing@example.com",
            "password": "WrongPassword!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_non_existent_email(self):
        """Should reject non-existent email with 401."""
        login_payload = {
            "email": "notfound@example.com",
            "password": "SomePassword123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Profile

    def test_profile_access_unauthenticated(self):
        """Should block anonymous requests to protected profile route with 401."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_access_authenticated(self):
        """Should allow access and return customized profile details with a valid bearer token."""
        # Authenticate the request by manually forcing it or passing credentials
        self.client.force_authenticate(user=self.existing_user)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.existing_user.username)
        self.assertIn("date_join", response.data)

    # Logout

    def test_successful_logout_blacklists_token(self):
        """Should accept a valid active refresh token, blacklist it, and return 205."""
        self.client.force_authenticate(user=self.existing_user)

        # Generate real SimpleJWT tokens for our test user
        refresh = RefreshToken.for_user(self.existing_user)
        logout_payload = {"refresh": str(refresh)}

        response = self.client.post(self.logout_url, logout_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_with_invalid_or_expired_token(self):
        """Should fail with 400 when attempting to blacklist a garbage/corrupted token string."""
        self.client.force_authenticate(user=self.existing_user)
        logout_payload = {"refresh": "this-is-not-a-valid-jwt-token-string"}

        response = self.client.post(self.logout_url, logout_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
