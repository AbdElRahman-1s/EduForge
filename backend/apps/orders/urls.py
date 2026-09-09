from django.urls import path

from .views import CheckoutView, StripeWebhookView

urlpatterns = [
    path(
        "courses/<int:course_id>/checkout/",
        CheckoutView.as_view(),
        name="course-checkout",
    ),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
