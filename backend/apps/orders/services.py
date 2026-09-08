from django.conf import settings
from django.db import transaction

from . import gateways
from .models import Order


def _format_url(template, course_id):
    if "{course_id}" in template:
        return template.format(course_id=course_id)
    return template


def create_checkout_session(*, student, course):
    """Create a fresh checkout order and return it with its Stripe URL."""
    with transaction.atomic():
        Order.objects.filter(
            student=student,
            course=course,
            status=Order.Status.PENDING,
        ).update(status=Order.Status.EXPIRED)

        order = Order.objects.create(
            student=student, course=course, amount=course.price
        )

        try:
            session_id, checkout_url = gateways.create_checkout_session(
                order=order,
                course=course,
                student=student,
                success_url=_format_url(settings.STRIPE_SUCCESS_URL, course.pk),
                cancel_url=_format_url(settings.STRIPE_CANCEL_URL, course.pk),
            )
        except Exception:
            order.status = Order.Status.FAILED
            order.save(update_fields=["status", "updated_at"])
            raise

        order.provider_reference = session_id
        order.save(update_fields=["provider_reference", "updated_at"])
        return order, checkout_url
