from django.urls import path

from .views import CheckoutView

urlpatterns = [
    path(
        "courses/<int:course_id>/checkout/",
        CheckoutView.as_view(),
        name="course-checkout",
    ),
]
