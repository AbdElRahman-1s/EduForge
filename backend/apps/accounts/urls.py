from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path("register/", view=RegistrationView.as_view(), name="registeration"),
    path("login/", view=LoginView.as_view(), name="login"),
]
