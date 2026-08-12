from django.urls import path
from .views import EnrollmentCreateView, MyEnrollmentsView

urlpatterns = [
    path(
        "courses/<int:course_id>/enroll/", EnrollmentCreateView.as_view(), name="enroll"
    ),
    path("enrollments/mine/", MyEnrollmentsView.as_view(), name="my-enrollments"),
]
