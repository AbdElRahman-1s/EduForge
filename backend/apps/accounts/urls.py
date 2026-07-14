from django.urls import path
from .views import RegistrationView, LoginView, RefreshView, LogoutView, ProfileView

urlpatterns = [
    path("register/", view=RegistrationView.as_view(), name="registeration"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("token/refresh/", RefreshView.as_view(), name="refresh_token"),
]
