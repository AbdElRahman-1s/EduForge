from django.urls import path
from .views import CourseListCreateView, CourseDetailView, InstructorCourseListView

urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("mine/", InstructorCourseListView.as_view(), name="instructor-courses"),
]
