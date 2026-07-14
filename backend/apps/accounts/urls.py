from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistrationView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path("register/", view=RegistrationView.as_view(), name="registeration"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
]
