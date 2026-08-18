from django.urls import path
from .views import DashboardOverviewView

urlpatterns = [
    path("dashboard/", DashboardOverviewView.as_view(), name="dashboard-overview"),
]
