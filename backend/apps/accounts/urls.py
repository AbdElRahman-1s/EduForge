from django.urls import path
from .views import RegistrationView

urlpatterns = [
    path("register/", view=RegistrationView.as_view(), name="registeration"),
]
