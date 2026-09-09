"""Smoke-test the Stripe checkout + webhook flow against the live Stripe API.

Run from the backend dir with the venv active:

    .venv/Scripts/python.exe manage.py smoke_payments

Creates throwaway smoke data (student/course/order/enrollment) in the dev DB,
issues a real `POST /api/courses/{id}/checkout/` (real Stripe Checkout Session),
then forwards a locally-signed `checkout.session.completed` event to the webhook
and verifies order `paid` + active enrollment.
"""

import json
import time

import stripe
from django.conf import settings
from django.core.management.base import BaseCommand
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course
from apps.enrollments.models import Enrollment
from apps.orders.models import Order


def _mask(value):
    if not value:
        return "(missing)"
    if len(value) <= 12:
        return f"{value[:4]}…"
    return f"{value[:10]}…{value[-4:]}"


class Command(BaseCommand):
    help = "Smoke-test Stripe checkout + webhook fulfillment against the live API."

    def handle(self, *args, **options):
        self.write = self.stdout.write
        self.run()

    def _line(self, text, ok=None):
        if ok is True:
            self.write(self.style.SUCCESS(text))
        elif ok is False:
            self.write(self.style.ERROR(text))
        else:
            self.write(text)

    def run(self):
        self._line("Smoke test: Stripe payment integration", None)

        # 1. Environment -------------------------------------------------------
        secret = settings.STRIPE_SECRET_KEY
        webhook = settings.STRIPE_WEBHOOK_SECRET
        mode = "LIVE" if secret.startswith("sk_live_") else "TEST"
        self._line(f"STRIPE_SECRET_KEY     = {_mask(secret)}  [{mode}]")
        self._line(f"STRIPE_WEBHOOK_SECRET = {_mask(webhook)}")
        if not secret or not webhook:
            self._line("Aborting: Stripe keys are not configured.", False)
            return

        # Throwaway test data --------------------------------------------------
        instructor, _ = User.objects.get_or_create(
            username="smoke_instructor",
            defaults={
                "email": "smoke-instructor@example.com",
                "role": User.Role.INSTRUCTOR,
            },
        )
        category, _ = Category.objects.get_or_create(name="Smoke test")
        course, _ = Course.objects.get_or_create(
            instructor=instructor,
            title="Smoke Paid Course",
            defaults={
                "category": category,
                "description": "Smoke test course",
                "level": Course.CourseLevel.BEGINNER,
                "price": "49.00",
                "published": True,
            },
        )
        stamp = int(time.time())
        student = User.objects.create_user(
            username=f"smoke_student_{stamp}",
            email=f"smoke_student_{stamp}@example.com",
        )
        self._line(
            f"Test data: student={student.username}  course=#{course.pk}  "
            f"price={course.price}  published={course.published}"
        )

        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(student).access_token}"
        )

        # 2. Scenario 1 — live checkout session --------------------------------
        self._line(f"\n[1] POST /api/courses/{course.pk}/checkout/  (live Stripe API)")
        response = client.post(
            f"/api/courses/{course.pk}/checkout/",
            data=b"{}",
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self._line(f"    HTTP {response.status_code}")

        if response.status_code != 200:
            self._line(f"    body: {response.data}", False)
            return

        body = response.data
        order_id, checkout_url = body["order_id"], body["checkout_url"]
        self._line(f"    order_id     = {order_id}")
        self._line(f"    checkout_url = {checkout_url}")

        order = Order.objects.get(pk=order_id)
        self._line(
            f"    DB Order: status={order.status}  amount={order.amount}  "
            f"provider_reference={order.provider_reference}"
        )
        ok1 = (
            order.status == Order.Status.PENDING
            and order.amount == course.price
            and order.provider_reference.startswith("cs_")
            and checkout_url.startswith("https://checkout.stripe.com/")
        )
        self._line("    Scenario 1 " + ("PASS" if ok1 else "FAIL"), ok1)
        if not ok1:
            return

        # 3. Scenario 2 — signature-verified webhook fulfillment ---------------
        self._line(
            "\n[2] POST /api/webhooks/stripe/  "
            "(locally-signed checkout.session.completed)"
        )
        event_payload = json.dumps(
            {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": order.provider_reference,
                        "amount_total": int(order.amount * 100),
                    }
                },
            }
        )
        header = stripe.WebhookSignature.generate_signature_header(
            event_payload, settings.STRIPE_WEBHOOK_SECRET
        )
        wh_response = client.post(
            "/api/webhooks/stripe/",
            data=event_payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=header,
            HTTP_HOST="localhost",
        )
        self._line(f"    HTTP {wh_response.status_code}")

        order.refresh_from_db()
        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        self._line(f"    DB Order: status={order.status}")
        self._line(
            "    DB Enrollment: "
            + (
                f"active for {enrollment.student.username}"
                if enrollment
                else "NONE"
            )
        )
        ok2 = (
            wh_response.status_code == 200
            and order.status == Order.Status.PAID
            and enrollment is not None
            and enrollment.status == Enrollment.Status.ACTIVE
        )
        self._line("    Scenario 2 " + ("PASS" if ok2 else "FAIL"), ok2)
        if not ok2:
            return

        self._line("\nSmoke test PASSED — full Stripe flow verified end to end.")
