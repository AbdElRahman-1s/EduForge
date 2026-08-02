from django.db.models.aggregates import Max
from rest_framework import generics
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
)
from .models import Course, Category, Topic, Section
from .permissions import IsInstructor, IsCourseOwner

# Create your views here.


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
        if self.request.method == "GET":
            return Course.objects.filter(published=True)
        return Course.objects.all()

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
