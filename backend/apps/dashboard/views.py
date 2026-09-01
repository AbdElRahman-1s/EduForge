from datetime import timedelta

from django.db.models import Count, F, IntegerField, Min, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Lesson
from apps.courses.permissions import IsInstructor
from apps.enrollments.models import Enrollment
from apps.reviews.annotations import annotate_review_stats

from .serializers import (
    DashboardOverviewSerializer,
    InstructorCourseSerializer,
    InstructorStudentSerializer,
)


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
        courses = annotate_review_stats(
            request.user.courses.select_related("category").annotate(
                enrollment_count=Count(
                    "enrollments__student_id",
                    filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
                    distinct=True,
                ),
                lesson_count=Count("sections__lessons", distinct=True),
                total_duration=Coalesce(
                    Subquery(
                        Lesson.objects.filter(section__course=OuterRef("pk"))
                        .values("section__course")
                        .annotate(total=Sum("duration_seconds"))
                        .values("total")
                    ),
                    0,
                    output_field=IntegerField(),
                ),
            )
        ).order_by("-enrollment_count")

        serializer = InstructorCourseSerializer(instance=courses, many=True)
        return Response(serializer.data)


class InstructorStudentsView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request, *args, **kwargs):
        students = (
            Enrollment.objects.filter(course__instructor=request.user)
            .values(
                "student_id",
                username=F("student__username"),
                email=F("student__email"),
            )
            .annotate(
                course_count=Count("course", distinct=True),
                joined_at=Min("enrolled_at"),
            )
            .order_by("-course_count", "student_id")
        )

        serializer = InstructorStudentSerializer(instance=students, many=True)
        return Response(serializer.data)
