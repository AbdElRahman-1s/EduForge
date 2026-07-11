from django.urls import path
from .views import RegistrationView, LoginView, LogoutView

urlpatterns = [
    path("register/", view=RegistrationView.as_view(), name="registeration"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
