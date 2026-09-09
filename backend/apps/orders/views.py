from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment

from . import gateways, services


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        if (
            request.user.role == User.Role.INSTRUCTOR
            and course.instructor_id == request.user.id
        ):
            return Response(
                {"detail": "Instructors cannot purchase their own courses."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not course.published:
            return Response(
                {"detail": "Course is not published"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if course.price is None or course.price <= 0:
            return Response(
                {"detail": f"Course is free, use /api/courses/{course_id}/enroll/"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Enrollment.objects.filter(
            student=request.user, course=course, status=Enrollment.Status.ACTIVE
        ).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order, checkout_url = services.create_checkout_session(
            student=request.user, course=course
        )
        return Response(
            {"order_id": order.pk, "checkout_url": checkout_url},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """Public webhook — Stripe's signature header is the only credential."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            event = gateways.construct_event(
                payload=request.body,
                sig_header=request.META.get("HTTP_STRIPE_SIGNATURE"),
            )
        except ValueError:
            return Response(
                {"detail": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        services.handle_event(event)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)
