from django.db.models.aggregates import Max
from django.db.models import Q
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
from django.contrib.auth import get_user_model

# Create your views here.
User = get_user_model()


class CourseListCreateView(generics.ListCreateAPIView):

    def get_queryset(self):
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

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


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        queryset = Course.objects.filter(published=True)
        if (
            self.request.user.is_authenticated
            and self.request.user.role == User.Role.INSTRUCTOR
        ):
            queryset = Course.objects.filter(
                Q(published=True) | Q(instructor=self.request.user)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsInstructor(), IsCourseOwner()]


class InstructorCourseListView(generics.ListAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


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
