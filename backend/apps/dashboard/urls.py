from django.urls import path
from .views import DashboardOverviewView, InstructorCoursesView

urlpatterns = [
    path("dashboard/", DashboardOverviewView.as_view(), name="dashboard-overview"),
    path("courses/", InstructorCoursesView.as_view(), name="instructor-courses"),
]
