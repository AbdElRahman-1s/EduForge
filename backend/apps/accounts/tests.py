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
        self.refresh_url = reverse("refresh_token")

        self.user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "role": User.Role.STUDENT,
        }

        self.existing_user = User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="ExistingPassword123!",
            role=User.Role.INSTRUCTOR,
        )

    def _login_and_get_tokens(self):
        refresh = RefreshToken.for_user(self.existing_user)
        access = str(refresh.access_token)
        self.client.cookies["refresh"] = str(refresh)
        return str(refresh), access

    # Registration

    def test_successful_registration(self):
        """Should create a new user and return a 201 status code."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"], self.user_data["username"])
        self.assertEqual(response.data["user"]["role"], self.user_data["role"])
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
        """Should authenticate valid credentials, return access token, and set refresh cookie."""
        login_payload = {
            "email": "existing@example.com",
            "password": "ExistingPassword123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], login_payload["email"])
        self.assertEqual(response.data["user"]["role"], self.existing_user.role)
        self.assertIn("refresh", response.cookies)
        self.assertEqual(response.cookies["refresh"]["httponly"], True)
        self.assertEqual(response.cookies["refresh"]["path"], "/api/auth/")

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
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    # Profile

    def test_profile_access_unauthenticated(self):
        """Should block anonymous requests to protected profile route with 401."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_access_authenticated(self):
        """Should allow access and return the contract profile payload with a valid bearer token."""
        _, access = self._login_and_get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.existing_user.username)
        self.assertEqual(response.data["role"], self.existing_user.role)
        self.assertIn("date_joined", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)

    # Logout

    def test_successful_logout_blacklists_token(self):
        """Should blacklist the refresh cookie and return 205."""
        refresh = RefreshToken.for_user(self.existing_user)
        access = str(refresh.access_token)
        self.client.cookies["refresh"] = str(refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data["message"], "Logged out successfully.")
        self.assertIn("refresh", response.cookies)
        self.assertEqual(response.cookies["refresh"]["max-age"], 0)

    def test_logout_with_invalid_or_expired_token(self):
        """Should fail with 401 when the refresh cookie is missing or invalid."""
        refresh = RefreshToken.for_user(self.existing_user)
        access = str(refresh.access_token)
        self.client.cookies["refresh"] = "this-is-not-a-valid-jwt-token-string"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid refresh token.")

    # Refresh

    def test_successful_refresh(self):
        """Should read the refresh cookie and return a new access token."""
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.cookies["refresh"] = str(refresh)

        response = self.client.post(self.refresh_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_without_cookie(self):
        """Should reject refresh requests that do not include the refresh cookie."""
        response = self.client.post(self.refresh_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Refresh token not provided.")
