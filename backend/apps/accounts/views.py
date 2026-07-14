from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import (
    RegistrationSerializer,
    LoginSerializer,
    ProfileSerializer,
)
from .models import User

# Create your views here.


def get_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh, str(refresh.access_token)


class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = User.objects.filter(email=email).first()

        if user is not None:
            is_password_correct = user.check_password(password)
        else:
            is_password_correct = False

        if not is_password_correct:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh, access = get_token(user)
        response = Response(
            {
                "access": access,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/api/auth/",
            max_age=60 * 60 * 24 * 7,
        )
        return response


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh = request.COOKIES.get("refresh")
        if refresh is None:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = RefreshToken(refresh)

            return Response(
                {"access": str(token.access_token)},
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"detail": "Token is invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.COOKIES.get("refresh")
        if refresh is None:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            RefreshToken(refresh).blacklist()

        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_205_RESET_CONTENT,
        )
        response.delete_cookie(
            key="refresh",
            path="/api/auth/",
        )
        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
