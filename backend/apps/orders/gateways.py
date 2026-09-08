"""Stripe provider boundary.

This is the only module in the project allowed to `import stripe` — a future
payment-provider swap should touch nothing outside this file.
"""

import stripe
from django.conf import settings


def create_checkout_session(*, order, course, student, success_url, cancel_url):
    """Create a Stripe-hosted Checkout Session for `order` and return its id + url."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": course.title},
                    "unit_amount": int(order.amount * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            # order_id is the authoritative webhook lookup key
            "order_id": str(order.pk),
            "course_id": str(course.pk),
            "student_id": str(student.pk),
        },
    )
    return session.id, session.url
