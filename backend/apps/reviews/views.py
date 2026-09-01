from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment

from .models import Review
from .pagination import ReviewListPagination
from .permissions import IsReviewAuthor
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    pagination_class = ReviewListPagination

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        return Review.objects.filter(course=course).order_by("-created_at", "-id")

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        user = self.request.user

        if (
            user.role == User.Role.INSTRUCTOR
            and course.instructor_id == user.id
        ):
            raise ValidationError(
                {"detail": "Instructors cannot review their own courses."}
            )

        if not Enrollment.objects.filter(
            student=user, course=course, status=Enrollment.Status.ACTIVE
        ).exists():
            raise PermissionDenied(
                {"detail": "An active enrollment is required to review this course."}
            )

        if Review.objects.filter(student=user, course=course).exists():
            raise ValidationError(
                {"detail": "You have already reviewed this course."}
            )

        serializer.save(student=user, course=course)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "You have already reviewed this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewAuthor]
