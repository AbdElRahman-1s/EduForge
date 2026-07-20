from django.urls import path
from .views import CourseListCreateView

urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list"),
]
