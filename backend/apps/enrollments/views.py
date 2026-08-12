from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.courses.models import Course

from .serializers import EnrollmentSerializer, MyEnrollmentSerializer
from .models import Enrollment

User = get_user_model()

# Create your views here.


class EnrollmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        if (
            request.user.role == User.Role.INSTRUCTOR
            and course.instructor_id == request.user.id
        ):
            return Response(
                {"detail": "Instructors cannot enroll in their own courses"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not course.published:
            return Response(
                {"detail": "Course is not published"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if course.price > 0:
            return Response(
                {"detail": "Course is not free"}, status=status.HTTP_400_BAD_REQUEST
            )
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                enrollment = Enrollment.objects.create(
                    student=request.user, course=course
                )
        except IntegrityError:
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyEnrollmentSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Enrollment.objects.filter(student=self.request.user)
            .select_related("course", "course__category", "course__instructor")
            .annotate(
                total_lessons=Count("course__sections__lessons"),
                total_duration_seconds=Sum(
                    "course__sections__lessons__duration_seconds", default=0
                ),
            )
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK,
        )
