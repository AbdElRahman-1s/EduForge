from django.urls import path
from .views import EnrollmentCreateView

urlpatterns = [
    path(
        "courses/<int:course_id>/enroll/", EnrollmentCreateView.as_view(), name="enroll"
    ),
]
