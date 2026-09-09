from decimal import Decimal
from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Category, Course
from apps.enrollments.models import Enrollment
from apps.orders.models import Order


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
