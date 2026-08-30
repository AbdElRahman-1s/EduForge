from django.urls import path
from .views import DashboardOverviewView, InstructorCoursesView, InstructorStudentsView

urlpatterns = [
    path("dashboard/", DashboardOverviewView.as_view(), name="dashboard-overview"),
    path("courses/", InstructorCoursesView.as_view(), name="instructor-course-analytics"),
    path("students/", InstructorStudentsView.as_view(), name="instructor-students"),
]
