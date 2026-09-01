from django.db.models.aggregates import Max, Count, Sum
from django.db.models import Q, Prefetch
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    InstructorCourseSerializer,
    CategorySerializer,
    TopicSerializer,
    SectionSerializer,
    LessonSerializer,
    SectionReorderSerializer,
    LessonReorderSerializer,
)
from .services import reorder_sections, reorder_lessons
from .models import Course, Category, Topic, Section, Lesson
from .permissions import IsInstructor, IsCourseOwner
from apps.reviews.annotations import annotate_review_stats
from django.contrib.auth import get_user_model

# Create your views here.
User = get_user_model()


class CourseListCreateView(generics.ListCreateAPIView):

    def get_queryset(self):
        queryset = Course.objects.select_related(
            "instructor", "category"
        ).prefetch_related("topics")

        if self.request.method == "GET":
            return annotate_review_stats(
                queryset.filter(published=True)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseListSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        enrolled_course_ids = set()

        if self.request.user.is_authenticated:
            enrolled_course_ids = self.request.user.enrollments.values_list(
                "course_id", flat=True
            )

        context["enrolled_course_ids"] = enrolled_course_ids
        return context


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        filters = Q(published=True)
        if (
            self.request.user.is_authenticated
            and self.request.user.role == User.Role.INSTRUCTOR
        ):
            filters |= Q(instructor=self.request.user)

        queryset = (
            Course.objects.filter(filters)
            .select_related("instructor", "category")
            .prefetch_related(
                "topics",
                Prefetch(
                    "sections",
                    queryset=Section.objects.order_by("order").prefetch_related(
                        Prefetch("lessons", queryset=Lesson.objects.order_by("order"))
                    ),
                ),
            )
            .annotate(
                total_lessons=Count("sections__lessons"),
                total_duration_seconds=Sum(
                    "sections__lessons__duration_seconds", default=0
                ),
            )
        )
        return annotate_review_stats(queryset)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor(), IsCourseOwner()]

    def retrieve(self, request, *args, **kwargs):
        self.course = self.get_object()
        serializer = self.get_serializer(self.course)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method != "GET":
            return context

        course = self.course

        context["is_course_owner"] = (
            self.request.user.is_authenticated
            and course.instructor_id == self.request.user.id
        )
        context["is_enrolled"] = (
            self.request.user.is_authenticated
            and course.enrollments.filter(
                student=self.request.user, status="active"
            ).exists()
        )

        return context


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    pagination_class = None

    def get_queryset(self):
        return annotate_review_stats(
            Course.objects.filter(instructor=self.request.user)
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsInstructor]


class TopicView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated, IsInstructor]


class SectionView(generics.CreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        course = get_object_or_404(
            Course,
            pk=self.kwargs["course_id"],
            instructor=self.request.user,
        )

        max_order = Section.objects.filter(course=course).aggregate(
            max_order=Max("order")
        )["max_order"]

        next_order = (max_order or 0) + 1
        serializer.save(course=course, order=next_order)


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    lookup_url_kwarg = "section_id"

    def get_queryset(self):
        return Section.objects.filter(
            course_id=self.kwargs["course_id"], course__instructor=self.request.user
        ).order_by("order")


class LessonView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        section = get_object_or_404(
            Section, pk=self.kwargs["section_id"], course__instructor=self.request.user
        )
        max_order = Lesson.objects.filter(section=section).aggregate(
            max_order=Max("order")
        )["max_order"]
        next_order = (max_order or 0) + 1
        serializer.save(section=section, order=next_order)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    lookup_url_kwarg = "lesson_id"

    def get_queryset(self):
        section = get_object_or_404(
            Section, pk=self.kwargs["section_id"], course__instructor=self.request.user
        )
        return Lesson.objects.filter(section=section).order_by("order")


class SectionReorderView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def patch(self, request, course_id):
        serializer = SectionReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reorder_sections(
            course_id=course_id,
            instructor=request.user,
            order=serializer.validated_data["order"],
        )
        return Response(
            {"message": "Sections reordered successfully."},
            status=status.HTTP_200_OK,
        )


class LessonReorderView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def patch(self, request, section_id):
        serializer = LessonReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reorder_lessons(
            section=get_object_or_404(
                Section, pk=section_id, course__instructor=request.user
            ),
            order=serializer.validated_data["order"],
        )

        return Response(
            {"message": "Lessons reordered successfully."}, status=status.HTTP_200_OK
        )
