import threading
import time
from decimal import Decimal
from unittest.mock import Mock, patch

from django.db import close_old_connections
from django.db.utils import OperationalError
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course, Lesson, Section
from apps.enrollments.models import Enrollment
from apps.orders.models import Order
from apps.reviews.models import Review


def _completed_event(session_id, amount_total):
    return {
        "type": "checkout.session.completed",
        "data": {
            "object": {"id": session_id, "amount_total": amount_total}
        },
    }


def _payment_failed_event(session_id):
    return {
        "type": "checkout.session.payment_failed",
        "data": {"object": {"id": session_id}},
    }


class CheckoutAPITests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Orders")
        self.student = User.objects.create_user(
            username="student", email="student@example.com"
        )

    def _course(self, *, price="89.00", published=True, instructor=None):
        return Course.objects.create(
            instructor=instructor or self.instructor,
            category=self.category,
            title="Paid course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price=price,
            published=published,
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _checkout_url(self, course):
        return reverse("course-checkout", kwargs={"course_id": course.pk})

    def _mock_session(self, session_id="cs_test_123"):
        session = Mock()
        session.id = session_id
        session.url = f"https://checkout.stripe.com/c/pay/{session_id}"
        return session

    def test_anonymous_checkout_returns_401(self):
        course = self._course()
        response = self.client.post(self._checkout_url(course), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_paid_course_returns_checkout_url_and_creates_pending_order(self):
        course = self._course()
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            stripe.checkout.Session.create.return_value = self._mock_session()
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get()
        self.assertEqual(response.data["order_id"], order.pk)
        self.assertEqual(
            response.data["checkout_url"],
            "https://checkout.stripe.com/c/pay/cs_test_123",
        )
        self.assertEqual(order.student, self.student)
        self.assertEqual(order.course, course)
        self.assertEqual(order.amount, Decimal("89.00"))
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.provider_reference, "cs_test_123")

        kwargs = stripe.checkout.Session.create.call_args.kwargs
        self.assertEqual(kwargs["mode"], "payment")
        self.assertEqual(
            kwargs["line_items"][0]["price_data"]["unit_amount"], 8900
        )
        self.assertEqual(kwargs["metadata"]["order_id"], str(order.pk))
        self.assertEqual(kwargs["metadata"]["course_id"], str(course.pk))
        self.assertEqual(kwargs["metadata"]["student_id"], str(self.student.pk))

    def test_free_course_returns_400_and_creates_no_order(self):
        course = self._course(price="0.00")
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(Order.objects.count(), 0)
        stripe.checkout.Session.create.assert_not_called()

    def test_null_price_course_returns_400_not_500(self):
        course = self._course(price=None)
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        stripe.checkout.Session.create.assert_not_called()

    def test_unpublished_course_returns_400(self):
        course = self._course(published=False)
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        stripe.checkout.Session.create.assert_not_called()

    def test_instructor_cannot_checkout_own_course(self):
        course = self._course()
        self._auth(self.instructor)

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        stripe.checkout.Session.create.assert_not_called()

    def test_missing_course_returns_404(self):
        self._auth(self.student)
        url = reverse("course-checkout", kwargs={"course_id": 9999})

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        stripe.checkout.Session.create.assert_not_called()

    def test_already_enrolled_student_cannot_checkout(self):
        course = self._course()
        Enrollment.objects.create(student=self.student, course=course)
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        stripe.checkout.Session.create.assert_not_called()

    def test_suspended_enrollment_does_not_block_checkout(self):
        course = self._course()
        Enrollment.objects.create(
            student=self.student,
            course=course,
            status=Enrollment.Status.SUSPENDED,
        )
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            stripe.checkout.Session.create.return_value = self._mock_session()
            response = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)

    def test_second_attempt_expires_prior_pending_and_creates_fresh_one(self):
        course = self._course()
        self._auth(self.student)

        with patch("apps.orders.gateways.stripe") as stripe:
            stripe.checkout.Session.create.return_value = self._mock_session(
                "cs_test_first"
            )
            first = self.client.post(self._checkout_url(course), {}, format="json")

        with patch("apps.orders.gateways.stripe") as stripe:
            stripe.checkout.Session.create.return_value = self._mock_session(
                "cs_test_second"
            )
            second = self.client.post(
                self._checkout_url(course), {}, format="json"
            )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)

        orders = list(Order.objects.order_by("created_at"))
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].status, Order.Status.EXPIRED)
        self.assertEqual(orders[0].provider_reference, "cs_test_first")
        self.assertEqual(orders[1].status, Order.Status.PENDING)
        self.assertEqual(orders[1].provider_reference, "cs_test_second")
        self.assertEqual(second.data["order_id"], orders[1].pk)
        self.assertNotEqual(orders[0].pk, orders[1].pk)


class StripeWebhookTests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="webhook-instructor",
            email="wh-instructor@example.com",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Webhook")
        self.student = User.objects.create_user(
            username="wh-student", email="wh-student@example.com"
        )
        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Webhook course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="89.00",
            published=True,
        )

    def _order(self, *, status=Order.Status.PENDING, ref="cs_webhook_1"):
        return Order.objects.create(
            student=self.student,
            course=self.course,
            amount="89.00",
            status=status,
            provider_reference=ref,
        )

    def _deliver(self, event):
        with patch(
            "apps.orders.gateways.stripe.Webhook.construct_event",
            return_value=event,
        ):
            return self.client.post(
                reverse("stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test_sig",
            )

    def test_valid_event_marks_order_paid_and_enrolls(self):
        order = self._order(ref="cs_paid")

        response = self._deliver(_completed_event("cs_paid", 8900))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        enrollment = Enrollment.objects.get()
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)

    def test_replayed_event_on_paid_order_does_not_re_enroll(self):
        order = self._order(status=Order.Status.PAID, ref="cs_paid")
        Enrollment.objects.create(student=self.student, course=self.course)

        response = self._deliver(_completed_event("cs_paid", 8900))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_amount_mismatch_marks_order_failed_without_enrolling(self):
        order = self._order(ref="cs_wrong_amount")

        response = self._deliver(_completed_event("cs_wrong_amount", 9900))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.FAILED)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_payment_failed_marks_order_failed(self):
        order = self._order(ref="cs_failed")

        response = self._deliver(_payment_failed_event("cs_failed"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.FAILED)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_tampered_signature_returns_400(self):
        self._order(ref="cs_ignored")

        with patch(
            "apps.orders.gateways.stripe.Webhook.construct_event",
            side_effect=ValueError("bad signature"),
        ):
            response = self.client.post(
                reverse("stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="forged",
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Enrollment.objects.count(), 0)


class StripeWebhookConcurrencyTests(TransactionTestCase):
    """Two threads delivering the same event → one enrollment, one transition."""

    def test_duplicate_delivery_activates_exactly_once(self):
        instructor = User.objects.create_user(
            username="conc-instructor",
            email="conc-instructor@example.com",
            role=User.Role.INSTRUCTOR,
        )
        category = Category.objects.create(name="Concurrency")
        student = User.objects.create_user(
            username="conc-student", email="conc-student@example.com"
        )
        course = Course.objects.create(
            instructor=instructor,
            category=category,
            title="Concurrency course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="89.00",
            published=True,
        )
        Order.objects.create(
            student=student,
            course=course,
            amount="89.00",
            provider_reference="cs_dup",
        )
        event = _completed_event("cs_dup", 8900)

        barrier = threading.Barrier(2)
        statuses = []

        def deliver():
            # SQLite shared-cache hands a losing writer an immediate
            # `OperationalError: database table is locked` rather than waiting.
            # Retry like Stripe redelivers a non-2xx webhook: once the winner
            # commits, the retry sees the paid order and returns 200.
            close_old_connections()
            try:
                client = APIClient()
                barrier.wait(timeout=5)
                for _ in range(10):
                    try:
                        response = client.post(
                            reverse("stripe-webhook"),
                            data=b"{}",
                            content_type="application/json",
                            HTTP_STRIPE_SIGNATURE="test_sig",
                        )
                    except OperationalError:
                        time.sleep(0.01)
                        close_old_connections()
                        continue
                    statuses.append(response.status_code)
                    return
            finally:
                close_old_connections()

        # A single shared patch (not one per thread): concurrent patch()
        # contexts on the same target are unsafe and can restore the real
        # function under a still-running thread.
        with patch(
            "apps.orders.gateways.stripe.Webhook.construct_event",
            return_value=event,
        ):
            threads = [
                threading.Thread(target=deliver) for _ in range(2)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)

        self.assertEqual(sorted(statuses), [200, 200])
        order = Order.objects.get(provider_reference="cs_dup")
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(
            Enrollment.objects.filter(student=student, course=course).count(), 1
        )


class WebhookEntitlementIntegrationTests(APITestCase):
    """A paid student, enrolled via the webhook, is entitled like a free one."""

    def setUp(self):
        self.instructor = User.objects.create_user(
            username="paid-instructor",
            email="paid-instructor@example.com",
            role=User.Role.INSTRUCTOR,
        )
        self.category = Category.objects.create(name="Paid entitlement")
        self.student = User.objects.create_user(
            username="paid-student", email="paid-student@example.com"
        )
        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Paid entitlement course",
            description="Description",
            level=Course.CourseLevel.BEGINNER,
            price="79.00",
            published=True,
        )
        section = Section.objects.create(course=self.course, title="Section", order=1)
        self.lesson = Lesson.objects.create(
            section=section,
            title="Premium lesson",
            duration_seconds=300,
            video="https://cdn.example.com/premium.mp4",
            free=False,
            order=1,
        )
        self.order = Order.objects.create(
            student=self.student,
            course=self.course,
            amount="79.00",
            provider_reference="cs_paid_access",
        )
        self.detail_url = reverse("course-detail", args=[self.course.pk])
        self.reviews_url = reverse(
            "course-reviews", kwargs={"course_id": self.course.pk}
        )

    def _auth_as(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _deliver_completed(self):
        with patch(
            "apps.orders.gateways.stripe.Webhook.construct_event",
            return_value=_completed_event("cs_paid_access", 7900),
        ):
            return self.client.post(
                reverse("stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test_sig",
            )

    def _lesson_video(self, detail):
        return detail.data["sections"][0]["lessons"][0]["video"]

    def test_before_fulfillment_paid_course_is_locked(self):
        self._auth_as(self.student)

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertFalse(detail.data["is_enrolled"])
        self.assertIsNone(self._lesson_video(detail))

        review = self.client.post(self.reviews_url, {"rating": 4}, format="json")
        self.assertEqual(review.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 0)

    def test_webhook_fulfillment_unlocks_video_and_reviews(self):
        response = self._deliver_completed()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Enrollment.objects.count(), 1)

        self._auth_as(self.student)
        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertTrue(detail.data["is_enrolled"])
        self.assertEqual(
            self._lesson_video(detail), "https://cdn.example.com/premium.mp4"
        )

        review = self.client.post(
            self.reviews_url, {"rating": 4, "comment": "Worth it"}, format="json"
        )
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
