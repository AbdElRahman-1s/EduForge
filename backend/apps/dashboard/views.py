from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.permissions import IsInstructor
from apps.enrollments.models import Enrollment

from .serializers import DashboardOverviewSerializer, InstructorCourseSerializer


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request, *args, **kwargs):
        courses = request.user.courses
        cutoff = timezone.now() - timedelta(days=30)

        totals = courses.aggregate(
            total_courses=Count("id", filter=Q(published=True), distinct=True),
            total_students=Count(
                "enrollments__student_id",
                filter=Q(
                    published=True,
                    enrollments__status=Enrollment.Status.ACTIVE,
                ),
                distinct=True,
            ),
        )

        recent_courses = (
            courses.filter(Q(created_at__gte=cutoff) | Q(updated_at__gte=cutoff))
            .annotate(
                student_count=Count(
                    "enrollments__student_id",
                    filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                    distinct=True,
                )
            )
            .order_by("-updated_at", "-created_at", "-id")
        )

        recent_signups = (
            Enrollment.objects.filter(
                course__instructor=request.user,
                enrolled_at__gte=cutoff,
            )
            .select_related("student", "course")
            .order_by("-enrolled_at", "-id")
        )

        data = {
            **totals,
            "recent_courses": recent_courses,
            "recent_signups": recent_signups,
        }
        serializer = DashboardOverviewSerializer(instance=data)
        return Response(serializer.data)


class InstructorCoursesView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request, *args, **kwargs):
        courses = request.user.courses.annotate(
            enrollment_count=Count(
                "enrollments__student_id",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                distinct=True,
            ),
            lesson_count=Count("sections__lessons", distinct=True),
            total_duration=Sum("sections__lessons__duration_seconds", default=0),
        ).order_by("-enrollment_count")

        serializer = InstructorCourseSerializer(instance=courses, many=True)
        return Response(serializer.data)
