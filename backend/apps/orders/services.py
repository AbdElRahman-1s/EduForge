from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction

from apps.enrollments.models import Enrollment

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


def handle_event(event):
    """Apply a signature-verified Stripe event to the matching order."""
    # Stripe's construct_event() returns an Event (StripeObject), not a dict.
    event = event.to_dict() if hasattr(event, "to_dict") else event
    session = event["data"]["object"]
    if event["type"] == "checkout.session.completed":
        _handle_session_completed(session)
    elif event["type"] == "checkout.session.payment_failed":
        _handle_session_failed(session)


def _handle_session_failed(session):
    with transaction.atomic():
        Order.objects.filter(
            provider_reference=session.get("id"),
            status=Order.Status.PENDING,
        ).update(status=Order.Status.FAILED)


def _handle_session_completed(session):
    session_id = session.get("id")
    amount_total = session.get("amount_total")
    expected = (
        None if amount_total is None else Decimal(amount_total) / 100
    )
    with transaction.atomic():
        # Claim the order atomically: only a pending order whose snapshot
        # matches the charged amount can move to paid. Exactly one concurrent
        # delivery wins this single UPDATE.
        claimed = Order.objects.filter(
            provider_reference=session_id,
            status=Order.Status.PENDING,
            amount=expected,
        ).update(status=Order.Status.PAID)

        if claimed:
            order = Order.objects.get(provider_reference=session_id)
            _activate_enrollment(order)
            return

        if expected is not None:
            # Still pending here means the amount didn't match — flag it.
            Order.objects.filter(
                provider_reference=session_id, status=Order.Status.PENDING
            ).exclude(amount=expected).update(status=Order.Status.FAILED)


def _activate_enrollment(order):
    try:
        with transaction.atomic():
            Enrollment.objects.create(
                student=order.student,
                course=order.course,
                status=Enrollment.Status.ACTIVE,
            )
    except IntegrityError:
        # unique_together(student, course) backstop: already enrolled.
        pass
